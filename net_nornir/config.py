import pathlib

__all__ = [
    'DEFAULT_STORE_PATH'
]

DEFAULT_STORE_PATH = pathlib.Path.home().joinpath('.net_nornir').joinpath('data')

def load_config():
    
    pass