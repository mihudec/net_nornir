
from pydantic.typing import Any
from nornir.core.task import Result, Task
from nornir_netmiko import CONNECTION_NAME


def netmiko_get_config(
    task: Task,
    **kwargs: Any
    ) -> Result:

    net_connect = task.host.get_connection(connection=CONNECTION_NAME, configuration=task.nornir.config)

    raw_config = net_connect.send_command('show running-config')
    return Result(host=task.host, result={'raw_config': raw_config})