import unittest

from nornir.core.inventory import Inventory, Host, Group
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from netmiko import ConnectHandler
from tests import NetNornirTest


class TestInit(NetNornirTest):

    def test_direct_init(self):
        INVENTORY_DIR = self.RESOURCES_DIR.joinpath('sample-inventory-01')
        ssh_config_path = INVENTORY_DIR.joinpath('ssh_config.conf')
        nr = InitNornir(
            runner={
                "plugin": "threaded",
                "options": {
                    "num_workers": 100,
                }
            },
            inventory={
                "plugin": "SimpleInventory",
                "options": {
                    "host_file": INVENTORY_DIR.joinpath('hosts.yml'),
                    "group_file": INVENTORY_DIR.joinpath('groups.yml')
                }
            }
        )


if __name__ == '__main__':
    unittest.main()