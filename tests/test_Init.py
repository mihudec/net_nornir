import unittest

from nornir.core.inventory import Inventory, Host, Group
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from netmiko import ConnectHandler

from net_nornir.tasks import netmiko_get_facts
from net_nornir.utils.common import inventory_validate_interfaces
from tests import NetNornirTest


class TestInit(NetNornirTest):

    def test_direct_init(self):
        nr = self.NR
        inventory_validate_interfaces(nr.inventory)

        

if __name__ == '__main__':
    unittest.main()