#!/bin/bash

BASEDIR=$(dirname $(readlink -f "$0"))

FSM4RTC_HOME="$BASEDIR/FSM4RTC/OpenRTM-aist"

$FSM4RTC_HOME/examples/SimpleIO/ConsoleInComp -f $BASEDIR/rtc.conf -o "logger.log_level:DEBUG" -o "sdo.service.provider.enabled_services:ALL" -o "manager.local_service.modules:$FSM4RTC_HOME/src/ext/sdo/fsm4rtc_observer/.libs/ComponentObserverConsumer.so(ComponentObserverConsumerInit),$FSM4RTC_HOME/src/ext/sdo/extended_fsm/.libs/ExtendedFsmServiceProvider.so(ExtendedFsmServiceProviderInit)"

