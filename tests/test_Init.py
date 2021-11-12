import unittest

from nornir.core.inventory import Inventory, Host, Group
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from netmiko import ConnectHandler

from net_nornir.tasks import netmiko_get_config
from net_nornir.utils.common import inventory_validate_interfaces
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
                    "group_file": INVENTORY_DIR.joinpath('groups.yml'),
                    "defaults_file": INVENTORY_DIR.joinpath('defaults.yml')
                }
            }
        )

        inventory_validate_interfaces(nr.inventory)
        print(nr.inventory.hosts['CSW'].data['interfaces'])
        print(nr.inventory.hosts['CSW'].data['interfaces']['Vlan1'])
        result = nr.run(netmiko_send_command, command_string='show version')
        print(result['CSW'][0])
        config_result = nr.run(netmiko_get_config)
        print_result(config_result)


if __name__ == '__main__':
    unittest.main()