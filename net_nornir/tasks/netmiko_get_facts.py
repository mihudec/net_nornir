
import pathlib
from typing import Optional

from netmiko import BaseConnection

from pydantic.typing import Any, List, Literal, Dict
from nornir.core.task import Result, Task
from net_nornir.config import DEFAULT_STORE_PATH

from net_parser.config import IosConfigParser
from net_parser.ops.BaseOpsParsers import OpsParser

from net_nornir.utils import store_text, get_logger, get_parsed_config

logger = get_logger(name='NetNornir', verbosity=5)

CONNECTION_NAME = 'netmiko'

__all__ = [
    'netmiko_get_facts',
    'netmiko_get_outputs'
]

def netmiko_get_facts(
    task: Task,
    facts: List[Literal['config']] = ['config', 'neighbors', 'interfaces'],
    store_config: bool = False,
    store_config_dir: Optional[pathlib.Path] = None,
    **kwargs
) -> Result:
    
    failed = False
    changed = False
    gathered_facts = {}

    result_dict = {
        'host': task.host,
        'changed': changed,
        'failed': failed,
        'result': {
            
        },
        'facts': gathered_facts
    }

    logger.debug(msg=f"Getting connection for host {task.host.name}")
    net_connect: BaseConnection = task.host.get_connection(connection=CONNECTION_NAME, configuration=task.nornir.config)

    if not net_connect.is_alive():
        failed = True
        return Result(msg="Inactive_connection")

    if 'config' in facts:
        raw_config = net_connect.send_command(command_string='show running-config')
        gathered_facts['raw_config'] = raw_config

        
        parsed_config = get_parsed_config(host=task.host, config=raw_config)
        gathered_facts['parsed_config_obj'] = parsed_config
        gathered_facts['parsed_config_model'] = parsed_config.to_model()
    
        if store_config:
            store_config_dir = store_config_dir or task.host.get('default_store_path') or DEFAULT_STORE_PATH
            logger.debug(msg=f"Storing config for host {task.host.name} to {store_config_dir}")
            store_text(text=raw_config, filename=f"{task.host.name}.conf", dir_path=store_config_dir)
            store_text(text=gathered_facts['parsed_config_model'].yaml(exclude_none=True), filename=f"{task.host.name}.yml", dir_path=store_config_dir)

    if 'neighbors' in facts:
        command = "show cdp neighbors detail"
        raw_neighbors = net_connect.send_command(command_string=command)
        gathered_facts['neighbors'] = OpsParser(vendor='ios', command=command).parse(text=raw_neighbors)

    if 'interfaces' in facts:
        command = "show interfaces"
        raw_neighbors = net_connect.send_command(command_string=command)
        gathered_facts['interfaces'] = OpsParser(vendor='ios', command=command).parse(text=raw_neighbors)
    

    if 'facts' not in task.host.data.keys():
        task.host.data['facts'] = {}
    task.host.data['facts'].update(gathered_facts)

    return Result(**result_dict)

def netmiko_get_outputs(
    task: Task,
    commands: List[str] = [],
    store_output: bool = False,
    store_output_dir: Optional[pathlib.Path] = None,
    **kwargs
) -> Result:
    
    failed = False
    changed = False
    outputs = {}

    result_dict = {
        'host': task.host,
        'changed': changed,
        'failed': failed,
        'result': {
            
        },
        'outputs': outputs
    }

    logger.debug(msg=f"Getting connection for host {task.host.name}")
    net_connect: BaseConnection = task.host.get_connection(connection=CONNECTION_NAME, configuration=task.nornir.config)
    print(f"{net_connect.banner_timeout=} {net_connect.conn_timeout=}")
    if not net_connect.is_alive():
        failed = True
        return Result(msg="Inactive_connection")

    for command in commands:
        output = net_connect.send_command(command_string=command)
        if store_output:
            store_output_dir = store_output_dir or task.host.get('default_store_path') or DEFAULT_STORE_PATH
            store_text(text=output, filename=f"{task.host.name}_{command.replace(' ', '_')}.txt", dir_path=store_output_dir, insert_timestamp=False)
        outputs[command] = output


    return Result(**result_dict)