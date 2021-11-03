import unittest

from nornir.core.inventory import Inventory, Host, Group
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from netmiko import ConnectHandler

from net_nornir.tasks import netmiko_get_config

from tests import NetNornirTest




class TestNetmiko(NetNornirTest):

    def test_01(self):
        provider = {
            'host': 'CSW',
            'username': 'admin',
            'password': 'cisco',
            'device_type': 'cisco_ios',
            'ssh_config_file': r'/home/mhudec/Develop/GitHub/net_nornir/tests/resources/sample-inventory-01/ssh_config.conf'
        }
        with ConnectHandler(**provider) as device:
            result = device.send_command('show version')
            print(result)

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
        # print(nr.inventory.hosts['CSW'].connection_options['netmiko'].extras)
        result = nr.run(netmiko_send_command, command_string='show version')
        print(result['CSW'][0])
        config_result = nr.run(netmiko_get_config)
        print(config_result['CSW'][0])


if __name__ == '__main__':
    unittest.main()