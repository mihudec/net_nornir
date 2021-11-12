import unittest
from net_nornir.utils.common import query_raw_params
from tests import NetNornirTest

from net_nornir.utils.common import *
from net_templates.filters import NetFilters


filters = NetFilters()

class TestQueryParams(NetNornirTest):


    def test_01(self):
        raw_data = {
            "interfaces": {
                "Vlan1": {
                    "name": "Vlan1"
                }
            }
        }
        raw_result = query_raw_params(expression='interfaces', data=raw_data)
        print(raw_result)

        model = validate_data(data=raw_data, model='InterfaceContainerModel', many=False, serialize=False)
        interface_list = list(model.interfaces.values())
        print(interface_list)
        model_result = query_model_params(expression='interfaces.*.{name: name, description: description }', data=model)
        print(model_result)

if __name__ == '__main__':
    unittest.main()