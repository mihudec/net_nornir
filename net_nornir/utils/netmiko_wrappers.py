import re
from typing import Callable
import logging
from netmiko import BaseConnection

from pydantic.typing import Any, Dict, List, Literal, Tuple, Union

from net_nornir.exceptions import *
from net_nornir.utils.get_logger import get_logger

LOGGER = get_logger(name="NetmikoWrapper", verbosity=4, with_threads=True)

ConfigCommands = Union[str, List[str]]



# Common Check Functions

def is_cisco_ios_error_result(command: str, result: str, logger: logging.Logger = None):
    if "% Invalid input detected at '^' marker." in result:
        raise InvalidCommand
    if "% Ambiguous command:" in result:
        raise AmbiguousCommand
    # Interface Service Policy
    m = re.search(pattern=r"Policy map (?P<pm_name>\S+) is already attached", flags=re.MULTILINE, string=result)
    if m:
        msg = f"Different PolicyMap is already present on interface. PM: \'{m.group('pm_name')}\'"
        logger.warning(msg=msg)
        raise PolicyMapPresent(msg)


def is_error_result(command: str, result: str, logger: logging.Logger = None):
    pass

def check_connection(net_connect: BaseConnection, logger: logging.Logger = None):
    logger = logger or LOGGER
    if not isinstance(net_connect, BaseConnection):
        msg = f"Invalid ConnectionType, expected BaseConnection, got {type(net_connect)}"
        logger.error(msg=msg)
        raise TypeError(msg)
    else:
        logger.debug(msg=f"Got {type(net_connect)} connection.")
    return net_connect

def check_cisco_ios_result(command: str, result: str, logger: logging.Logger = None):
    is_cisco_ios_error_result(command=command, result=result, logger=logger)
    return result

def check_result(net_connect: BaseConnection, command: str, result: str, logger: logging.Logger = None):
    logger = logger or LOGGER

    device_type_mapping = {
        'cisco_ios': check_cisco_ios_result
    }

    verified_result = None

    if net_connect.device_type in device_type_mapping.keys():
        try:
            verified_result = device_type_mapping[net_connect.device_type](command=command, result=result, logger=logger)
        except InvalidCommand as e:
            msg = f"Invalid command on '{net_connect.host}': '{command}'"
            logger.warning(msg=msg)
            raise InvalidCommand(msg)
        except AmbiguousCommand as e:
            msg = f"Ambiguous command on '{net_connect.host}': '{command}'"
            logger.warning(msg=msg)
            raise AmbiguousCommand(msg)
        except PolicyMapPresent as e:
            raise 
        except Exception as e:
            raise
    else:
        is_error_result(command=command, result=result, logger=logger)
        verified_result = result
    return verified_result

def send_config(net_connect: BaseConnection, config_commands: ConfigCommands, logger: logging.Logger = None, **kwargs):
    logger = logger or LOGGER
    results = {}
    if isinstance(config_commands, str):
        config_commands = [config_commands]
    for config_command in config_commands:
        logger.debug(msg=f"Sending config command: '{config_command}' to host: '{net_connect.host}'")
        command_result = net_connect.send_config_set(config_commands=config_commands, **kwargs)
        command_result = check_result(net_connect=net_connect, command=config_command, result=command_result)
        results[config_command] = command_result
    return results

def send_command(net_connect: BaseConnection, command_string: str, logger: logging.Logger = None, **kwargs):
    logger = logger or LOGGER
    logger.debug(msg=f"Sending command: '{command_string}' to host: '{net_connect.host}'")
    result = net_connect.send_command(command_string=command_string, **kwargs)
    result = check_result(net_connect=net_connect, command=command_string, result=result)
    return result
    
