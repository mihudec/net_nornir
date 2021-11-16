import functools
import pathlib

import jmespath

from pydantic.typing import Any, Callable, Dict, List, Literal, Union

from nornir.core.task import Result, Task


from net_models.inventory.ConfigDefaults import ConfigDefaults
from net_models.models.BaseModels.BaseNetModels import BaseNetModel
from net_templates.templar import TemplarBase

from net_nornir.utils.common import *


TEMPLAR = TemplarBase()

class ParamsSpec(object):
    """This class serves as a container for the specfications
    required to fetch data from inventory 

    """

    def __init__(
        self, 
        path: str, 
        filter_spec: Dict[str, Any] = None,
        func: Callable = None,
        serialize: bool = True
    ) -> None:
        """Just a container class to make life easier

        Args:
            path (str): JMESPath expression to fetch all data from inventory
            filter_spec (Dict[str, Any], optional): Dictionary used as filter when serializing pydantic models.
                `See here <https://pydantic-docs.helpmanual.io/usage/exporting_models/>`_ Defaults to None.
            func (Callable, optional): Currently not used, in future might be used for lambda functions to further process data. Defaults to None.
            serialize (bool, optional): Wether or not produce serialized dictionaries or keep original types. Defaults to True.
        """
        self.path = path
        self.filter_spec = filter_spec
        self.func = func
        self.serialize = serialize


class TemplateDataFetcher(object):
    def __init__(
        self,
        task: Task,
        params_spec: Dict[str, ParamsSpec],
    ) -> None:
        """Class to actually fetch data from inventory

        Args:
            task (Task): Nornir Task object providing access to host data
            params_spec (Dict[str, ParamsSpec]): Dictionary - values are ParamsSpec object 
            specifying where and how to get the data.
        """
        self.task = task
        self.data = task.host.data
        self.params_spec = params_spec

    def get_data(self) -> Dict[str, Any]:
        """Fetch the data from inventory, filter them, serialize if needed and return.

        Returns:
            Dict[str, Any]: Data to be fed to template
        """
        host_data = self.data
        # Get data from path
        params = {k: None for k in self.params_spec.keys()}
        for key in self.params_spec.keys():
            params_spec = self.params_spec[key]
            expression = params_spec.path
            data = jmespath.search(expression=expression, data=host_data)
            
            if params_spec.filter_spec is not None:

                if isinstance(data, dict):
                    if all([isinstance(x, BaseNetModel) for x in data.values()]):
                        print("Dict of Models")
                        if params_spec.serialize:
                            data = {k: v.serial_dict(**params_spec.filter_spec) for k,v in data.items()}
                        else:
                            data = {k: v.dict(**params_spec.filter_spec) for k,v in data.items()}
                    elif all([isinstance(x, dict) for x in data.values()]):
                        print("Dict of Dicts")
                if isinstance(data, list):
                    if all([isinstance(x, BaseNetModel) for x in data]):
                        print("List of Models")
                        if params_spec.serialize:
                            data = [x.serial_dict(**params_spec.filter_spec) for x in data]
                        else:
                            data = [x.dict(**params_spec.filter_spec) for x in data]
                    elif all([isinstance(x, dict) for x in data]):
                        print("List of Dicts")
            params[key] = data
        return params


@functools.lru_cache
def get_jinja_environment(device_type: str, extra_template_dirs: List[pathlib.Path] = None):
    device_type_map = {
        'cisco_ios': 'ios'
    }
    env = TEMPLAR.get_device_type_environment(device_type=device_type_map[device_type])
    if extra_template_dirs:
        for path in extra_template_dirs:
            TEMPLAR.extend_searchpath(env=env, path=path)
    return env


def render_template(
    template_name: str,
    data: Any,
    device_type: Literal['cisco_ios'],
    extra_template_dirs: List[pathlib.Path] = None,
    global_params: Union[ConfigDefaults, Dict] = None

) -> str:
    env = get_jinja_environment(device_type=device_type, extra_template_dirs=extra_template_dirs)
    template = env.get_template(name=template_name)

    if isinstance(data, TemplateDataFetcher):
        data = data.get_data()
    
    if not global_params:
        global_params = ConfigDefaults()
    if isinstance(global_params, ConfigDefaults):
        global_params = global_params.dict()

    params = dict(global_params)
    params.update(data)
    output = template.render(**params)
    return output
    