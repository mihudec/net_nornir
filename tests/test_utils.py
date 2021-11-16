from enum import unique
import unittest
from unittest.mock import Mock
from build.lib import net_nornir
from net_nornir.utils.common import inventory_validate_interfaces
from tests import NetNornirTest

from net_nornir.exceptions import *
from net_nornir.utils.netmiko_wrappers import *
from net_nornir.utils.config import get_config_diff, get_parsed_config
from net_nornir.utils.template import TemplateDataFetcher, ParamsSpec, render_template


class TestConfigUtils(NetNornirTest):

    def get_working_connection(self):
        host = self.NR.inventory.hosts['CSW']
        CONNECTION_NAME = 'netmiko'
        net_connect = host.get_connection(connection=CONNECTION_NAME, configuration=self.NR.config)
        return net_connect

    def test_get_parsed_config_from_device(self):
        host = self.NR.inventory.hosts['CSW']
        net_connect = self.get_working_connection()
        raw_config = send_command(net_connect=net_connect, command_string="show running-config", logger=self.TEST_LOGGER)
        parsed_config = get_parsed_config(host=host, config=raw_config, config_defaults={})
        print(parsed_config)
    
    def test_get_parsed_config_from_raw(self):
        host = self.NR.inventory.hosts['CSW']
        net_connect = self.get_working_connection()
        raw_config = [
            "interface Vlan1",
            " cdp enable"
        ]
        parsed_config = get_parsed_config(host=host, config=raw_config, device_type='cisco_ios', config_defaults={})
        print(parsed_config)

    def test_diff(self):
        host = self.NR.inventory.hosts['CSW']
        net_connect = self.get_working_connection()
        desired_raw_config = [
            "interface Vlan1",
            " cdp enable"
        ]
        desired_parsed_config = get_parsed_config(host=host, config=desired_raw_config, device_type='cisco_ios', config_defaults={})
        current_raw_config = send_command(net_connect=net_connect, command_string="show running-config", logger=self.TEST_LOGGER)
        current_parsed_config = get_parsed_config(host=host, config=current_raw_config, config_defaults={})

        diff = get_config_diff(first=current_parsed_config, second=desired_parsed_config)
        diff_lines = diff.difference()
        diff.print_diff(diff_lines)
        self.assertEqual([x.text for x in diff_lines], ["interface Vlan1", " cdp enable"])

class MockTask(Mock):
    
    pass
    
class TestDataFetcher(NetNornirTest):

    def test_template_data_fetcher(self):
        mock_task = MockTask()
        host = self.NR.inventory.hosts['CSW']
        inventory_validate_interfaces(self.NR.inventory)
        mock_task.host = host

        tdf = TemplateDataFetcher(
            task=mock_task,
            params_spec={
                'params': ParamsSpec(
                    path="interfaces",
                    filter_spec={
                        'include': {'name', 'description', 'enabled'}
                    },
                    serialize=True
                )
            }
        )
        print(tdf.get_data())
        print(render_template(template_name='ios_interfaces.j2', data=tdf, device_type='cisco_ios'))
        