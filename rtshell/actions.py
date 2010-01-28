# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtsshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: actions.py

Function objects for actions that can be performed using rtctree.

'''

__version__ = '$Revision: $'
# $Source$


from rtctree.exceptions import NoSuchConfSetError, NoSuchConfParamError
from rtctree.path import parse_path
from rtsshell.exceptions import RequiredActionFailedError
from rtsshell.options import Options


###############################################################################
## Base action function object

class Action(object):
    '''Base class for all action function objects.

    Action objects should implement the _execute method. This will receive one
    argument (a reference to the RTCTree object) and should implement the
    action. It must return True for success or False for failure, and a very
    brief error message.

    Action objects must implement the __str__ method. They should print out a
    description of what they will do. This description should include details
    specific to that instance of the action (for example, 'Will activate
    component 'ConsoleIn0.rtc'').

    '''

    def __init__(self):
        pass

    def __call__(self, rtctree):
        result, err = self._execute(rtctree)
        if not result:
            print 'Action failed.'
        if err:
            print err

    def __str__(self):
        return 'Base action'

    def _execute(self, rtctree):
        '''Base for action execution method.

        Return (True, '') or (False, 'Why I failed.') when implementing this
        method.

        '''
        raise NotImplementedError


###############################################################################
## Required action function object base

class RequiredAction(Action):
    '''Base class for action function objects that must succeed.

    Action objects that inherit from this class will raise an error if they
    fail. The error will be @ref RequiredActionFailedError.

    '''
    def __init__(self):
        super(RequiredAction, self).__init__()

    def __call__(self, rtctree):
        result, err = self._execute(rtctree)
        if not result:
            raise RequiredActionFailedError(err)


###############################################################################
## Decorator to turn a required action into an optional action

class OptionalAction(Action):
    '''Decorator to turn a required action into an optional action.

    If the wrapped action fails, its failure will be ignored.

    '''
    def __init__(self, action_type, args):
        super(OptionalAction, self).__init__()
        self._wrapped_action = action_type(*args)

    def __str__(self):
        return '(Optional) ' + str(self._wrapped_action)

    def _execute(self, rtctree):
        result, err = self._wrapped_action._execute(rtctree)
        return True, err


###############################################################################
## Check if a required component is present

class CheckForRequiredCompAct(RequiredAction):
    '''Check for a required component in the RTC Tree.

    This action checks the rtctree to see if a component is present at a
    particular path. If it finds a component at that path, it will check that
    the component's ID and instance name to ensure it is the desired component.
    If the component is not present or is the wrong component, this action will
    fail. Otherwise, it will succeed.

    '''
    def __init__(self, path_str, id, instance_name):
        super(CheckForRequiredCompAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._id = id
        self._instance_name = instance_name

    def __str__(self):
        return 'Check for required component "{0}", "{1}" at path {2}'.format(\
                self._id, self._instance_name, self._path_str)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Checking for required component {0} with ID "{1}" and \
instance name "{2}"'.format(self._path_str, self._id, self._instance_name)
        # Check there is a component at the specified path
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, \
                    'Required component missing: {0}'.format(self._path_str)
        # Check the instance names match
        if comp.instance_name != self._instance_name:
            return False, 'Component instance names mismatched: {0} != \
{1}'.format(comp.instance_name, self._instance_name)
        # Check the IDs match - in rtctree, the ID is formed from like so:
        # 'RTC:'<vendor>:<category>:<type_name>:<version>
        id = 'RTC:{0}:{1}:{2}:{3}'.format(comp.vendor, comp.category,
                                          comp.type_name, comp.version)
        if id != self._id:
            return False, 'Component IDs mismatched: {0} != {1}'.format(id,
                    self._id)
        # All good
        return True, None


###############################################################################
## Check if a port exists on a component

class CheckForPortAct(RequiredAction):
    '''Check for a port on a component in the RTC Tree.

    This action checks the rtctree to see if a component is present at a
    particular path. If it finds a component at that path, it will check that
    the component has the desired port. If the port is not present on the
    component, it will fail. Otherwise, it will succeed. No check is performed
    to ensure that the correct component is at that path; for that, use the
    @ref CheckForRequiredCompAct action.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, port_name):
        super(CheckForPortAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._port_name = port_name

    def __str__(self):
        return 'Check for required port "{0}" on component at path \
{1}'.format(self._port_name, self._path_str)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Checking for required port {0} on component {1}'.format(\
                    self._port_name, self._path_str)
        # Get the component at the specified path
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return True, None
        # Check for the port
        if not comp.has_port_by_name(self._port_name):
            return False, \
                    'Required port not found: {0}'.format(self._port_name)
        # All good
        return True, None


###############################################################################
## Set the active configuration set of a component

class SetActiveConfigSetAct(RequiredAction):
    '''Set the active configuration set of a component.

    This action sets the active configuration set of a component to the
    specified configuration set. It will check if the set exists first; if no
    such set exists, the action will fail.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set):
        super(SetActiveConfigSetAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA

    def __str__(self):
        return 'Set configuration set "{0}" active on component at path \
{1}'.format(self._set, self._path_str)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Setting configuration set "{0}" active on component \
{1}'.format(self._set, self._path_str)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        try:
            comp.activate_conf_set(self._set)
        except NoSuchConfSetError:
            return False, 'Invalid configuration set: {0}'.format(self._set)
        return True, None


###############################################################################
## Set a configuration parameter in a configuration set

class SetConfigParamValueAct(RequiredAction):
    '''Change the value of a configuration parameter in a set.

    This action sets the value of the given configuration parameter in the
    given configuration set. It will fail if the set does not exist, or the
    parameter does not exist in that set.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set, parameter, new_value):
        super(SetConfigParamValueAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA
        self._param = str(parameter)
        self._new_value = str(new_value)

    def __str__(self):
        return 'Set parameter "{0}" in set "{1}" on component at path "{2}" \
to "{3}"'.format(self._param, self._set, self._path_str, self._new_value)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Setting parameter "{0}" in set "{1}" on component at path \
"{2}" to "{3}"'.format(self._param, self._set, self._path_str, self._new_value)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        try:
            comp.set_conf_set_value(self._set, self._param, self._new_value)
        except NoSuchConfSetError:
            return False, 'Invalid configuration set: {0}'.format(self._set)
        except NoSuchConfParamError:
            return False, 'Invalid configuration parameter: {0}'.format(self._param)
        if self._set == comp.active_conf_set_name:
            comp.activate_conf_set(self._set)
        return True, None

###############################################################################
## Connect two ports

class ConnectPortsAct(RequiredAction):
    '''Connect two ports together.

    This action connects two ports together using the provided connection
    profile. It will fail if either the components or the ports ports are not
    present. No check is made to ensure the components at the specified paths
    are the correct components.

    '''
    def __init__(self, source_path, source_port, dest_path, dest_port,
                 name, id, properties):
        super(ConnectPortsAct, self).__init__()
        self._source_path_str = source_path
        self._source_path = parse_path(source_path)[0]
        self._source_port = source_port
        self._dest_path_str = dest_path
        self._dest_path = parse_path(dest_path)[0]
        self._dest_port = dest_port
        self._name = name
        self._id = id
        self._properties = properties.copy()

    def __str__(self):
        return 'Connect {0}:{1} to {2}:{3} with properties {4}'.format(\
                self._source_path_str, self._source_port,
                self._dest_path_str, self._dest_port,
                self._properties)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Connecting {0}:{1} to {2}:{3}'.format(\
                    self._source_path_str, self._source_port,
                    self._dest_path_str, self._dest_port)
        source_comp = rtctree.get_node(self._source_path)
        if not source_comp or not source_comp.is_component:
            return False, 'Source component missing: {0}'.format(\
                    self._source_path_str)
        source_port_obj = source_comp.get_port_by_name(self._source_port)
        if not source_port_obj:
            return False, 'Source port missing: {0}:{1}'.format(\
                    self._source_path_str, self._source_port)
        dest_comp = rtctree.get_node(self._dest_path)
        if not dest_comp or not dest_comp.is_component:
            return False, 'Destination component missing: {0}'.format(\
                    self._dest_path_str)
        dest_port_obj = dest_comp.get_port_by_name(self._dest_port)
        if not dest_port_obj:
            return False, 'Destination port missing: {0}:{1}'.format(\
                    self._dest_path_str, self._dest_port)

        source_port_obj.connect(dest_port_obj, name=self._name, id=self._id,
                                props=self._properties)
        return True, None


###############################################################################
## Disconnect two data ports

class DisconnectPortsAct(RequiredAction):
    '''Disconnect two ports.

    This action disconnects two ports. It will fail if either the components or
    the ports ports are not present. No check is made to ensure the components
    at the specified paths are the correct components.

    '''
    def __init__(self, source_path, source_port, dest_path, dest_port):
        super(DisconnectPortsAct, self).__init__()
        self._source_path_str = source_path
        self._source_path = parse_path(source_path)[0]
        self._source_port = source_port
        self._dest_path_str = dest_path
        self._dest_path = parse_path(dest_path)[0]
        self._dest_port = dest_port

    def __str__(self):
        return 'Disconnect {0}:{1} from {2}:{3}'.format(self._source_path_str,
                self._source_port, self._dest_path_str, self._dest_port)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Disconnecting {0}:{1} from {2}:{3}'.format(\
                    self._source_path_str, self._source_port,
                    self._dest_path_str, self._dest_port)
        source_comp = rtctree.get_node(self._source_path)
        if not source_comp or not source_comp.is_component:
            return False, 'Source component missing: {0}'.format(\
                    self._source_path_str)
        source_port_obj = source_comp.get_port_by_name(self._source_port)
        if not source_port_obj:
            return False, 'Source port missing: {0}:{1}'.format(\
                    self._source_path_str, self._source_port)
        dest_comp = rtctree.get_node(self._dest_path)
        if not dest_comp or not dest_comp.is_component:
            return False, 'Destination component missing: {0}'.format(\
                    self._dest_path_str)
        dest_port_obj = dest_comp.get_port_by_name(self._dest_port)
        if not dest_port_obj:
            return False, 'Destination port missing: {0}:{1}'.format(\
                    self._dest_path_str, self._dest_port)

        conn = source_port_obj.get_connection_by_dest(dest_port_obj)
        if not conn:
            return False, 'No connection between {0}:{1} and {2}:{3}'.format(\
                    self._source_path_str, self._source_port,
                    self._dest_path_str, self._dest_port)
        conn.disconnect()
        return True, None


###############################################################################
## Activate a component

class ActivateCompAct(RequiredAction):
    '''Activate a component.

    This action changes the status of a component to active.

    '''
    def __init__(self, path_str, ec_id):
        super(ActivateCompAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._ec_id = ec_id

    def __str__(self):
        return 'Activate {0} in execution context {1}'.format(self._path_str,
                                                              self._ec_id)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Activating {0} in {1}'.format(self._path_str, self._ec_id)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        ec_index = comp.get_ec_index(int(self._ec_id))
        if ec_index < 0:
            return False, 'Invalid execution context: {0}'.format(self._ec_id)
        comp.activate_in_ec(ec_index)
        return True, None


###############################################################################
## Deactivate a component

class DeactivateCompAct(RequiredAction):
    '''Deactivate a component.

    This action changes the status of a component to inactive.

    '''
    def __init__(self, path_str, ec_id):
        super(DeactivateCompAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._ec_id = ec_id

    def __str__(self):
        return 'Deactivate {0} in execution context {1}'.format(self._path_str,
                                                                self._ec_id)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Deactivating {0} in {1}'.format(self._path_str, self._ec_id)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        ec_index = comp.get_ec_index(int(self._ec_id))
        if ec_index < 0:
            return False, 'Invalid execution context: {0}'.format(self._ec_id)
        comp.deactivate_in_ec(ec_index)
        return True, None


###############################################################################
## Reset a component

class ResetCompAct(RequiredAction):
    '''Reset a component.

    This action changes the status of a component to inactive from error.

    '''
    def __init__(self, path_str, ec_id):
        super(ResetCompAct, self).__init__()
        self._path_str = path_str
        self._path = parse_path(path_str)[0]
        self._ec_id = ec_id

    def __str__(self):
        return 'Reset {0} in execution context {1}'.format(self._path_str,
                                                           self._ec_id)

    def _execute(self, rtctree):
        if Options().verbose:
            print 'Resetting {0} in {1}'.format(self._path_str, self._ec_id)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        ec_index = comp.get_ec_index(int(self._ec_id))
        if ec_index < 0:
            return False, 'Invalid execution context: {0}'.format(self._ec_id)
        comp.reset_in_ec(ec_index)
        return True, None


# vim: tw=79

