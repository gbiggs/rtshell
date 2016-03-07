# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2015
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

Function objects for actions that can be performed using rtctree.

'''

from __future__ import print_function

import sys

import rtctree.exceptions as rtc_exceptions
import rtctree.path

from rtshell import option_store
from rtshell import rts_exceptions


###############################################################################
## Base action function object

class Action(object):
    '''Base class for all action function objects.

    Action objects should implement the _execute method. This will receive one
    argument (a reference to the RTCTree object) and should implement the
    action. It must return True for success or False for failure, and a very
    brief error message.

    All actions must be provided with one or more result callback objects.
    These will be called in the order they are set after performing the action
    and passed the result of the action's _execute method. Its job is to take
    appropriate measures based on the outcome of the action. Typically, the
    first should perform a verification that the result meets necessary
    criteria, such as a required action succeeding. If no callbacks are
    provided, a default (@ref BaseCallback) will be inserted.

    Action objects must implement the __str__ method. They should print out a
    description of what they will do. This description should include details
    specific to that instance of the action (for example, "Will activate
    component 'ConsoleIn0.rtc'").

    '''

    def __init__(self, callbacks=[]):
        super(Action, self).__init__()
        self._callbacks = callbacks

    def __call__(self, rtctree=None):
        result, err = self._execute(rtctree)
        if not self._callbacks:
            c = BaseCallback()
            c(result, err)
        else:
            for c in self._callbacks:
                c(result, err)

    def __str__(self):
        return 'Base action'

    def add_callback(self, callback):
        self._callbacks.append(callback)

    @property
    def optional(self):
        '''Is this action optional?'''
        for cb in self._callbacks:
            if cb.__class__ == RequiredActionCB:
                return False
        return True

    def _action_string(self, action_desc):
        if self._callbacks:
            action_desc += ' ({0}'.format(self._callbacks[0])
            for c in self._callbacks[1:]:
                action_desc += ', {0}'.format(c)
            action_desc += ')'
        return action_desc

    def _execute(self, rtctree):
        '''Base for action execution method.

        Return (True, '') or (False, 'Why I failed.') when implementing this
        method.

        '''
        raise NotImplementedError


###############################################################################
## Base callback

class BaseCallback(object):
    '''Base class for callback objects.

    Callback objects must implement the __call__ method, and receive two
    values:
    - A boolean indicating success or failure of the action.
    - An error message to optionally be printed on failure. None if no message.

    '''
    def __init__(self, *args, **kwargs):
        super(BaseCallback, self).__init__()

    def __call__(self, result, err_msg):
        if err_msg:
            if not result:
                print('Action failed: ' + err_msg, file=sys.stderr)
        else:
            if not result:
                print('Action failed.', file=sys.stderr)

    def __str__(self):
        return ''


###############################################################################
## Required action callback

class RequiredActionCB(BaseCallback):
    '''Callback for a required action.

    Checks the action result and raises @ref RequiredActionFailedError if the
    action failed.

    '''
    def __init__(self, *args, **kwargs):
        super(RequiredActionCB, self).__init__(*args, **kwargs)

    def __call__(self, result, err_msg):
        if not result:
            raise rts_exceptions.RequiredActionFailedError(err_msg)

    def __str__(self):
        return 'Required'


###############################################################################
## Check if a required component is present

class CheckForRequiredCompAct(Action):
    '''Check for a required component in the RTC Tree.

    This action checks the rtctree to see if a component is present at a
    particular path. If it finds a component at that path, it will check that
    the component's ID and instance name to ensure it is the desired component.
    If the component is not present or is the wrong component, this action will
    fail. Otherwise, it will succeed.

    '''
    def __init__(self, path_str, id, instance_name, callbacks=[]):
        super(CheckForRequiredCompAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._id = id
        self._instance_name = instance_name

    def __str__(self):
        return self._action_string('Check for required component \
"{0}", "{1}" at path {2}'.format(self._id, self._instance_name,
                self._path_str))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Checking for required component {0} with ID \
"{1}" and instance name "{2}"'.format(self._path_str, self._id,
                    self._instance_name), file=sys.stderr)
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

class CheckForPortAct(Action):
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
    def __init__(self, path_str, port_name, callbacks=[]):
        super(CheckForPortAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._port_name = port_name

    def __str__(self):
        return self._action_string('Check for required port "{0}" on \
component at path {1}'.format(self._port_name, self._path_str))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Checking for required port {0} on component \
{1}'.format(self._port_name, self._path_str), file=sys.stderr)
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
## Check the active configuration set of a component.

class CheckActiveConfigSetAct(Action):
    '''Checks if a configuration set is active in a component.

    This action checks if the active configuration set of a component is as
    expected. It will check if the set exists first; if no such set exists,
    the action will fail.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set, callbacks=[]):
        super(CheckActiveConfigSetAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA

    def __str__(self):
        return self._action_string('Check configuration set "{0}" is active '\
                'on component {1}'.format(self._set, self._path_str))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Checking configuration set "{0}" is active '\
                    'on component {1}'.format(self._set, self._path_str),
                    file=sys.stderr)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        if comp.active_conf_set_name != self._set:
            return False, 'Wrong configuration set is active on {0} '\
                    '(Active set: {1})'.format(self._path_str,
                            comp.active_conf_set_name)
        return True, None


###############################################################################
## Set the active configuration set of a component

class SetActiveConfigSetAct(Action):
    '''Set the active configuration set of a component.

    This action sets the active configuration set of a component to the
    specified configuration set. It will check if the set exists first; if no
    such set exists, the action will fail.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set, callbacks=[]):
        super(SetActiveConfigSetAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA

    def __str__(self):
        return self._action_string('Set configuration set "{0}" active on \
component at path {1}'.format(self._set, self._path_str))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Setting configuration set "{0}" active on \
component {1}'.format(self._set, self._path_str), file=sys.stderr)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        try:
            comp.activate_conf_set(self._set)
        except rts_exceptions.NoConfSetError:
            return False, 'Invalid configuration set: {0}'.format(self._set)
        return True, None


###############################################################################
## Set a configuration parameter in a configuration set

class CheckConfigParamAct(Action):
    '''Check the value of a configuration parameter.

    This action checks that the value of a configuration parameter is correct.
    It will fail if the set or the parameter does not exist.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set, param, value, callbacks=[]):
        super(CheckConfigParamAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA
        self._param = str(param)
        self._value = str(value)

    def __str__(self):
        return self._action_string('Check parameter "{0}" in set "{1}" on '\
                'component at path "{2}" is "{3}"'.format(self._param,
                    self._set, self._path_str, self._value))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Checking parameter "{0}" in set "{1}" on '\
                    'component "{2}" is "{3}"'.format(self._param, self._set,
                            self._path_str, self._value), file=sys.stderr)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        if not self._set in comp.conf_sets:
            return False, 'Invalid configuration set: {0}'.format(self._set)
        if not comp.conf_sets[self._set].has_param(self._param):
            return False, 'Invalid configuration parameter: '\
                    '{0}'.format(self._param)
        if comp.conf_sets[self._set].data[self._param] != self._value:
            return False, 'Configuration parameter {0} in set {1} on '\
                    'component {2} is incorrect (value: {3})'.format(
                            self._param, self._set, self._path_str,
                            comp.conf_sets[self._set].data[self._param])
        return True, None


###############################################################################
## Set a configuration parameter in a configuration set

class SetConfigParamValueAct(Action):
    '''Change the value of a configuration parameter in a set.

    This action sets the value of the given configuration parameter in the
    given configuration set. It will fail if the set does not exist, or the
    parameter does not exist in that set.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, path_str, set, parameter, new_value, callbacks=[]):
        super(SetConfigParamValueAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._path = rtctree.path.parse_path(path_str)[0]
        self._set = str(set) # Cannot send unicode strings to CORBA
        self._param = str(parameter)
        self._new_value = str(new_value)

    def __str__(self):
        return self._action_string('Set parameter "{0}" in set "{1}" on \
component at path {2} to "{3}"'.format(self._param, self._set,
                self._path_str, self._new_value))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Setting parameter "{0}" in set "{1}" on \
component at path {2} to "{3}"'.format(self._param, self._set,
                    self._path_str, self._new_value), file=sys.stderr)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        try:
            comp.set_conf_set_value(self._set, self._param, self._new_value)
        except rts_exceptions.NoConfSetError:
            return False, 'Invalid configuration set: {0}'.format(self._set)
        except rtc_exceptions.NoSuchConfParamError:
            return False, 'Invalid configuration parameter: {0}'.format(self._param)
        comp.reparse_conf_sets()
        if self._set == comp.active_conf_set_name:
            comp.activate_conf_set(self._set)
        return True, None


###############################################################################
## Check if a connection between two components exists and is correct

class CheckForConnAct(Action):
    '''Check for a correct connection between two components.

    This action checks if there is a connection between the specified source
    and destination ports. If there is, it will check that any given properties
    are also correct.

    No check is performed to ensure that the correct component is at that path;
    for that, use the @ref CheckForRequiredCompAct action.

    This action will not fail if the specified component does not exist or is
    incorrect. To cause an abort in these situations, use @ref
    CheckForRequiredCompAct.

    '''
    def __init__(self, source, dest, id, props={}, callbacks=[]):
        super(CheckForConnAct, self).__init__(callbacks=callbacks)
        self._source = source
        self._s_path = rtctree.path.parse_path(self._source[0])[0]
        self._dest = dest
        self._d_path = rtctree.path.parse_path(self._dest[0])[0]
        self._id = id
        self._props = props

    def __str__(self):
        return self._action_string('Check for connection from {0}:{1} to ' \
                '{2}:{3} with properties {4}'.format(self._source[0],
                    self._source[1], self._dest[0], self._dest[1],
                    self._props))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Checking for connection between {0}:{1} and ' \
                    '{2}:{3}'.format(self._source[0], self._source[1],
                            self._dest[0], self._dest[1]))
        # Get the source component
        s_comp = rtctree.get_node(self._s_path)
        if not s_comp or not s_comp.is_component:
            return False, 'Source component missing: {0}'.format(\
                    self._source[0])
        s_port = s_comp.get_port_by_name(self._source[1])
        if not s_port:
            return False, 'Source port missing: {0}:{1}'.format(\
                    self._source[0], self._source[1])
        # Get the destination component
        d_comp = rtctree.get_node(self._d_path)
        if not d_comp or not d_comp.is_component:
            return False, 'Destination component missing: {0}'.format(\
                    self._dest[0])
        d_port = d_comp.get_port_by_name(self._dest[1])
        if not d_port:
            return False, 'Destination port missing: {0}:{1}'.format(\
                    self._dest[0], self._dest[1])

        conn = s_port.get_connection_by_id(self._id)
        if not conn:
            # No connection: fail
            return False, 'No connection between {0}:{1} and {2}:{3}'.format(
                    self._source[0], self._source[1], self._dest[0],
                    self._dest[1])
        conn = d_port.get_connection_by_id(self._id)
        if not conn:
            # No connection: fail
            return False, 'No connection between {0}:{1} and {2}:{3}'.format(
                    self._source[0], self._source[1], self._dest[0],
                    self._dest[1])
        # Check the properties
        for k in self._props:
            if self._props[k] != conn.properties[k]:
                return False, 'Property {0} of connection from {1}:{2} to '\
                        '{3}:{4} is incorrect.'.format(k, self._source[0],
                                self._source[1], self._dest[0], self._dest[1])

        # All good
        return True, None


###############################################################################
## Connect two ports

class ConnectPortsAct(Action):
    '''Connect two ports together.

    This action connects two ports together using the provided connection
    profile. It will fail if either the components or the ports ports are not
    present. No check is made to ensure the components at the specified paths
    are the correct components.

    '''
    def __init__(self, source_path, source_port, dest_path, dest_port,
                 name, id, properties, callbacks=[]):
        super(ConnectPortsAct, self).__init__(callbacks=callbacks)
        self._source_path_str = source_path
        self._source_path = rtctree.path.parse_path(source_path)[0]
        self._source_port = source_port
        self._dest_path_str = dest_path
        self._dest_path = rtctree.path.parse_path(dest_path)[0]
        self._dest_port = dest_port
        self._name = name
        self._id = id
        self._properties = properties.copy()

    def __str__(self):
        return self._action_string('Connect {0}:{1} to {2}:{3} with \
ID {4} and properties {5}'.format(self._source_path_str, self._source_port,
                self._dest_path_str, self._dest_port, self._id,
                self._properties))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Connect {0}:{1} to {2}:{3} with \
ID {4} and properties {5}'.format(self._source_path_str, self._source_port,
                    self._dest_path_str, self._dest_port, self._id,
                    self._properties), file=sys.stderr)
        source_comp = rtctree.get_node(self._source_path)
        if not source_comp or not source_comp.is_component:
            return False, 'Source component missing: {0}'.format(\
                    self._source_path_str)
        s_port = source_comp.get_port_by_name(self._source_port)
        if not s_port:
            return False, 'Source port missing: {0}:{1}'.format(\
                    self._source_path_str, self._source_port)
        dest_comp = rtctree.get_node(self._dest_path)
        if not dest_comp or not dest_comp.is_component:
            return False, 'Destination component missing: {0}'.format(\
                    self._dest_path_str)
        d_port = dest_comp.get_port_by_name(self._dest_port)
        if not d_port:
            return False, 'Destination port missing: {0}:{1}'.format(\
                    self._dest_path_str, self._dest_port)

        conn = s_port.get_connection_by_id(self._id)
        if not conn:
            if d_port.get_connection_by_id(self._id) is None:
                # No existing connection
                s_port.connect([d_port], name=self._name, id=self._id,
                                        props=self._properties)
                return True, None
            else:
                # The destination port has a connection with that ID but
                # different ports.
                return False, \
                    'Destination port has existing connection with ID {0}'.format(
                            self._id)
        else:
            if len(conn.ports) != 2 or not conn.has_port(d_port):
                # The source port has a connection with that ID but different
                # ports.
                return False, \
                    'Source port has existing connection with ID {0}'.format(
                            self._id)
            else:
                # The connection already exists - check the properties match
                for k in self._properties:
                    if self._properties[k] != conn.properties[k]:
                        return False, \
                                'Property {0} of existing connection from '\
                                '{1}:{2} to {3}:{4} with ID {5} does not '\
                                'match'.format(k, self._source_path_str,
                                        self._source_port, self._dest_path_str,
                                        self._dest_port, self._id)
                if option_store.OptionStore().verbose:
                    print('Skipped existing connection with ID {0}'.format(
                                    self._id), file=sys.stderr)
                return True, None


###############################################################################
## Disconnect two data ports

class DisconnectPortsAct(Action):
    '''Disconnect two ports.

    This action disconnects two ports. It will fail if either the components or
    the ports ports are not present. No check is made to ensure the components
    at the specified paths are the correct components.

    '''
    def __init__(self, source_path, source_port, dest_path, dest_port, id,
                 callbacks=[]):
        super(DisconnectPortsAct, self).__init__(callbacks=callbacks)
        self._source_path_str = source_path
        self._source_path = rtctree.path.parse_path(source_path)[0]
        self._source_port = source_port
        self._dest_path_str = dest_path
        self._dest_path = rtctree.path.parse_path(dest_path)[0]
        self._dest_port = dest_port
        self._id = id

    def __str__(self):
        return self._action_string('Disconnect {0}:{1} from {2}:{3} with ID {4}'.format(\
                self._source_path_str, self._source_port, self._dest_path_str,
                self._dest_port, self._id))

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print('Disconnecting {0}:{1} from {2}:{3} with ID {4}'.format(\
                    self._source_path_str, self._source_port,
                    self._dest_path_str, self._dest_port, self._id),
                    file=sys.stderr)
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

        s_conn = source_port_obj.get_connection_by_id(self._id)
        if not s_conn:
            return False, 'No connection from {0}:{1} with ID {2}'.format(
                    self._source_path_str, self._source_port, self._id)
        d_conn = dest_port_obj.get_connection_by_id(self._id)
        if not d_conn:
            return False, 'No connection to {0}:{1} with ID {2}'.format(
                    self._dest_path_str, self._dest_port, self._id)
        s_conn.disconnect()
        return True, None


###############################################################################
## State change base action

class StateChangeAct(Action):
    '''Base action for actions that change a component's state.

    Actions that inherit from this should provide three members:
    - self._action_str: A string describing the action for use in str(). e.g.
      "Activate".
    - self._verbose_str: A similar string for use in the verbose output. e.g.
      "Activating".
    - self._action_impl: A function to be called by self._execute to perform
      the action. It will be passed two arguments; the first is the component
      node from rtctree, the second is the index of the execution context
      involved. This should return (True, None) or False and an error string.

    '''
    def __init__(self, path_str, comp_id, instance_name, ec_id, callbacks=[]):
        super(StateChangeAct, self).__init__(callbacks=callbacks)
        self._path_str = path_str
        self._comp_id = comp_id
        self._instance_name = instance_name
        self._path = rtctree.path.parse_path(path_str)[0]
        self._ec_id = ec_id

    def __str__(self):
        return self._action_string('{0} {1} in execution context {2}'.format(\
                self._action_str, self._path_str, self._ec_id))

    @property
    def comp_id(self):
        '''Identification string of the component.'''
        return self._comp_id

    @property
    def ec_id(self):
        '''Target execution context ID.'''
        return self._ec_id

    @property
    def instance_name(self):
        '''Instance name of the target component.'''
        return self._instance_name

    @property
    def path(self):
        '''Full path of the target component.'''
        return self._path_str

    def _execute(self, rtctree):
        if option_store.OptionStore().verbose:
            print((self._verbose_str, self._path_str, self._ec_id),
                    file=sys.stderr)
        comp = rtctree.get_node(self._path)
        if not comp or not comp.is_component:
            return False, 'Component missing: {0}'.format(self._path_str)
        ec_index = comp.get_ec_index(int(self._ec_id))
        if ec_index < 0:
            return False, 'Invalid execution context: {0}'.format(self._ec_id)
        return self._action_impl(comp, ec_index)


###############################################################################
## Check component state

class CheckCompStateAct(StateChangeAct):
    '''Check component state in an execution context.

    This action checks that the state of an execution context is as expected.

    '''
    def __init__(self, path_str, comp_id, instance_name, ec_id, expected,
            callbacks=[]):
        super(CheckCompStateAct, self).__init__(path_str, comp_id,
                instance_name, ec_id, callbacks=callbacks)
        self._expected = expected
        self._action_str = 'Check state is {0} for'.format(self._expected)
        self._verbose_str = 'Checking state is {0} for'.format(self._expected)

    def _action_impl(self, comp, ec_index):
        if (self._expected.lower() == 'active' and \
                comp.state_in_ec(ec_index) == comp.ACTIVE) or \
            (self._expected.lower() == 'inactive' and \
                comp.state_in_ec(ec_index) == comp.INACTIVE) or \
            (self._expected.lower() == 'error' and \
                comp.state_in_ec(ec_index) == comp.ERROR) or \
            (self._expected.lower() == 'created' and \
                comp.state_in_ec(ec_index) == comp.CREATED) or \
            (self._expected.lower() == 'unknown' and \
                comp.state_in_ec(ec_index) == comp.UNKNOWN):
            return True, None
        return False, 'Component {0} is in incorrect state {1}'.format(
                self._path_str,
                comp.get_state_in_ec_string(ec_index, add_colour=False))


###############################################################################
## Activate a component

class ActivateCompAct(StateChangeAct):
    '''Activate a component.

    This action changes the status of a component to active.

    '''
    def __init__(self, path_str, comp_id, instance_name, ec_id, callbacks=[]):
        super(ActivateCompAct, self).__init__(path_str, comp_id, instance_name,
                ec_id, callbacks=callbacks)
        self._action_str = 'Activate'
        self._verbose_str = 'Activating'

    def _action_impl(self, comp, ec_index):
        comp.activate_in_ec(ec_index)
        return True, None


###############################################################################
## Deactivate a component

class DeactivateCompAct(StateChangeAct):
    '''Deactivate a component.

    This action changes the status of a component to inactive.

    '''
    def __init__(self, path_str, comp_id, instance_name, ec_id, callbacks=[]):
        super(DeactivateCompAct, self).__init__(path_str, comp_id,
                instance_name, ec_id, callbacks=callbacks)
        self._action_str = 'Deactivate'
        self._verbose_str = 'Deactivating'

    def _action_impl(self, comp, ec_index):
        comp.deactivate_in_ec(ec_index)
        return True, None


###############################################################################
## Reset a component

class ResetCompAct(StateChangeAct):
    '''Reset a component.

    This action changes the status of a component to inactive from error.

    '''
    def __init__(self, path_str, comp_id, instance_name, ec_id, callbacks=[]):
        super(ResetCompAct, self).__init__(path_str, comp_id, instance_name,
                ec_id, callbacks=callbacks)
        self._action_str = 'Reset'
        self._verbose_str = 'Resetting'

    def _action_impl(self, comp, ec_index):
        comp.reset_in_ec(ec_index)
        return True, None


# vim: tw=79

