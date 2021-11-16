import unittest
import pathlib

from nornir import InitNornir

from net_nornir.utils.get_logger import get_logger

class NetNornirTest(unittest.TestCase):

    RESOURCES_DIR = pathlib.Path(__file__).resolve().parent.joinpath('resources')
    INVENTORY_DIR = RESOURCES_DIR.joinpath('sample-inventory-01')
    TEST_LOGGER = get_logger(name="TestLogger", verbosity=5, with_threads=True)


    def setUp(self) -> None:
        self.NR = InitNornir(
            runner={
                "plugin": "threaded",
                "options": {
                    "num_workers": 100,
                }
            },
            inventory={
                "plugin": "SimpleInventory",
                "options": {
                    "host_file": self.INVENTORY_DIR.joinpath('hosts.yml'),
                    "group_file": self.INVENTORY_DIR.joinpath('groups.yml'),
                    "defaults_file": self.INVENTORY_DIR.joinpath('defaults.yml')
                }
            }
        )
        return super().setUp()