from unittest import result
from build.lib import net_nornir
from tests import NetNornirTest

from net_nornir.exceptions import *
from net_nornir.utils.netmiko_wrappers import *


class TestNetmikoWrappers(NetNornirTest):

    def get_working_connection(self):
        host = self.NR.inventory.hosts['CSW']
        CONNECTION_NAME = 'netmiko'
        net_connect = host.get_connection(connection=CONNECTION_NAME, configuration=self.NR.config)
        return net_connect

    def test_send_command_valid(self):
        net_connect = self.get_working_connection()
        commands = [
            "show version",
            "show running-config"
        ]
        for command_string in commands:
            with self.subTest(msg=f"Command: {command_string}"):
                result = send_command(net_connect=net_connect, command_string=command_string, logger=self.TEST_LOGGER)
                self.assertIsInstance(result, str)

    def test_send_command_invalid(self):
        net_connect = self.get_working_connection()
        command_string = "show versiom"
        with self.assertRaises(InvalidCommand):
            result = send_command(net_connect=net_connect, command_string=command_string, logger=self.TEST_LOGGER)

    def test_send_config_valid(self):
        net_connect = self.get_working_connection()
        result = send_config(net_connect=net_connect, config_commands='interface Vlan1', logger=self.TEST_LOGGER)

    def test_InvalidCommand(self):
        net_connect = self.get_working_connection()
        config_commands_list = [
            ["interface NonExistent1", 'description Does Not Exist']
        ]
        for config_commands in config_commands_list:
            with self.subTest(msg=f"Commands: {config_commands}"):
                with self.assertRaises(InvalidCommand):
                    result = send_config(net_connect=net_connect, config_commands='interface NonExistent1', logger=self.TEST_LOGGER)

    def test_PolicyMapPresent(self):
        net_connect = self.get_working_connection()
        with self.assertRaises(PolicyMapPresent):
            result = send_config(net_connect=net_connect, config_commands=['interface Vlan1', 'service-policy input PM-TEST-02'], logger=self.TEST_LOGGER)
        
