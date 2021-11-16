import datetime
import pathlib

from pydantic.typing import Dict, Any, Union, List, Type
from nornir.core.inventory import Host, Inventory
from net_templates.filters import NetFilters

from net_nornir.config import DEFAULT_STORE_PATH


NET_FILTERS = NetFilters()

__all__ = [
    'store_text',
    'validate_data',
    'inventory_validate_interfaces',
    'inventory_generate_host'
]

validate_data = NET_FILTERS.to_model

def get_timestamp():
    timestamp = datetime.datetime.utcnow()
    return timestamp.isoformat().replace(":", "")

def store_text(text: str, filename: str, dir_path: pathlib.Path, insert_timestamp: bool = True) -> pathlib.Path:
    if dir_path is None:
        dir_path = DEFAULT_STORE_PATH
    if not isinstance(dir_path, pathlib.Path):
        dir_path = pathlib.Path(dir_path).resolve()
    dir_path.mkdir(exist_ok=True)
    if insert_timestamp:
        if '.' in filename:
            name, suffix = filename.split('.')
            filename = f"{name}_{get_timestamp()}.{suffix}"
        else:
            filename = f"{filename}_{get_timestamp()}"
    path = dir_path.joinpath(filename)
    with path.open(mode='w') as f:
        f.write(text)
    return path

def inventory_validate_interfaces(inventory: Inventory) -> None:
    for host_name, host in inventory.hosts.items():
        interfaces = host.data.get('interfaces')
        if interfaces is not None:
            interfaces = validate_data(data={'interfaces': interfaces}, model='InterfaceContainerModel', many=False, serialize=False).interfaces
            host.data['interfaces'] = interfaces


def inventory_generate_host(inventory: Inventory):
    for host_name, host in inventory.hosts.items():
        if host.hostname is None:
            host.hostname = host.name
