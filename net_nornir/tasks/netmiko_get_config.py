
import pathlib
from pydantic.typing import Any
from nornir.core.task import Result, Task
from nornir_netmiko import CONNECTION_NAME
from net_nornir.config import DEFAULT_STORE_PATH

from net_parser.config import IosConfigParser

from net_nornir.utils import store_text, get_logger

logger = get_logger(name='NetNornir')

def netmiko_get_config(
    task: Task,
    store_config: bool = False,
    store_config_path: pathlib.Path = None,
    **kwargs: Any
    ) -> Result:


    logger.info(msg=f"{task.host.name}: Getting connection")
    net_connect = task.host.get_connection(connection=CONNECTION_NAME, configuration=task.nornir.config)

    result = {}
    failed = True

    raw_config = net_connect.send_command('show running-config')
    config = IosConfigParser(config=raw_config.split('\n'))
    config.parse()
    config_model = None
    try:
        config_model = config.to_model()
        failed=False
    except Exception as e:
        logger.error(msg=f"{task.host.name}: Failed to parse config. Exception: {repr(e)}")
    

    task.host.data['config_model'] = config_model

    if store_config:
        if store_config_path is None:
            if task.host.get('default_store_path') is not None:
                store_config_path = task.host.get('default_store_path') or DEFAULT_STORE_PATH
                store_text(text=raw_config, dir_path=store_config_path, filename=f"{task.host.name}.conf", insert_timestamp=True)
                if config_model is not None:
                    store_text(text=config_model.yaml(exclude_none=True), dir_path=store_config_path, filename=f"{task.host.name}.yml", insert_timestamp=True)
    
    
    return Result(
        host=task.host,
        result={
            'raw_config': raw_config,
            'store_path': store_config_path,
            'config_model': config_model
        },
        failed=failed,
        changed=False
    )