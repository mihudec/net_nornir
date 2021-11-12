import unittest


from tests import NetNornirTest

from nornir import InitNornir


from net_nornir.utils import query_raw_params
from net_nornir.tasks import template_generic

class TestTemplate(NetNornirTest):

    def get_nr(self):
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
        return nr


    # def test_query_params(self):
    #     nr = self.get_nr()
    #     host = nr.inventory.hosts['CSW']
    #     nr = nr.filter(name='CSW')
    #     print(nr.inventory.hosts)
    #     result = nr.run(query_raw_params, expression="interfaces.Vlan1")
    #     print(result['CSW'][0])


    def test_template_config(self):
        nr = self.get_nr()
        
        result = nr.run(template_generic, template_name='ios_interfaces.j2', params_spec={'params': 'interfaces'})


if __name__ == '__main__':
    unittest.main()