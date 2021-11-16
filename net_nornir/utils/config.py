import pathlib
from pydantic.typing import Any, Dict, List, Literal, Optional, Type, Union 

from nornir.core.inventory import Host

from net_models.inventory.ConfigDefaults import *
from net_parser.config import *


def get_config_parser_class(device_type: str) -> Type[BaseConfigParser]:
    parser_class_mapping = {
        'cisco_ios': IosConfigParser
    }
    if device_type in parser_class_mapping.keys():
        return parser_class_mapping[device_type]
    else:
        return BaseConfigParser

def get_parsed_config(host: Host, config: Union[str, List[str], pathlib.Path], device_type: str = None, config_defaults: Dict = None) -> BaseConfigParser:
    
    # TODO: Fix this
    device_type = device_type or 'cisco_ios'

    HOST_CONFIG_DEFAULTS = host.get('CONFIG_DEFAULTS')
    config_defaults = config_defaults or HOST_CONFIG_DEFAULTS

    if isinstance(config_defaults, ConfigDefaults):
        config_defaults = config_defaults
    elif isinstance(config_defaults, dict):
        config_defaults = ConfigDefaults.parse_obj(config_defaults)
    else:
        config_defaults = ConfigDefaults()

    PARSER_CLASS = get_config_parser_class(device_type=device_type)

    parsed_config = PARSER_CLASS(config=config)
    parsed_config.DEFAULTS = config_defaults
    parsed_config.parse()

    return parsed_config

def get_config_diff(first: BaseConfigParser, second: BaseConfigParser) -> ConfigDiff:
    d = ConfigDiff(first=first, second=second)
    return d
