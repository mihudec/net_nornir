import pathlib
import unittest


# from tests import NetNornirTest

from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from net_models import inventory
from net_models.inventory import ConfigDefaults
from net_nornir.tasks import netmiko_get_facts

from net_nornir.utils import query_raw_params, inventory_validate_interfaces
from net_nornir.tasks import template_generic, template_interfaces

# class TestTemplate(NetNornirTest):
#     pass

def get_nr():
    RESOURCES_DIR = pathlib.Path(__file__).resolve().parent.joinpath('resources')
    INVENTORY_DIR = RESOURCES_DIR.joinpath('sample-inventory-01')
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
    return nr


    # def test_query_params(self):
    #     nr = self.get_nr()
    #     host = nr.inventory.hosts['CSW']
    #     nr = nr.filter(name='CSW')
    #     print(nr.inventory.hosts)
    #     result = nr.run(query_raw_params, expression="interfaces.Vlan1")
    #     print(result['CSW'][0])


def test_template_config():
    nr = get_nr()
    inventory_validate_interfaces(inventory=nr.inventory)
    CONFIG_DEFAULTS = ConfigDefaults()
    CONFIG_DEFAULTS.INCLUDE_DEFAULTS = True
    CONFIG_DEFAULTS.INTERFACES_DEFAULT_NO_SHUTDOWN = True
    # result = nr.run(template_generic, template_name='ios_interfaces.j2', params_spec={'params': 'interfaces'}, global_params=CONFIG_DEFAULTS)
    result = nr.run(template_interfaces, model_params={'include': {'name', 'description'}}, global_params=CONFIG_DEFAULTS)
    result.raise_on_error()
    print_result(result=result)

def test_netmiko_get_facts():
    nr = get_nr()
    # inventory_validate_interfaces(nr.inventory)
    result = nr.run(netmiko_get_facts, store_config=True)
    print_result(result=result)
    result.raise_on_error()
    print(nr.inventory.hosts['CSW'].data['facts']['parsed_config_model'].yaml(exclude_none=True))
    host_data = nr.inventory.hosts['CSW'].data

def main():
    test_template_config()
    # test_netmiko_get_facts()

if __name__ == '__main__':
    main()