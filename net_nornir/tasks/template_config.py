import pathlib
import jinja2

from pydantic.typing import List, Dict, Union
from nornir.core.task import Result, Task

import jmespath


from net_models.inventory import ConfigDefaults
from net_templates.templar import TemplarBase

from net_nornir.utils.get_logger import get_logger
from net_nornir.utils.common import query_raw_params

TEMPLAR = TemplarBase()
LOGGER = get_logger(name="NetNornir")

def extend_jinja_env(env: jinja2.Environment, extra_template_dirs: List[pathlib.Path] = None) -> None:
    if extra_template_dirs is not None:
        for templates_dir in extra_template_dirs:
            TEMPLAR.extend_searchpath(env=env, path=templates_dir)

def get_jinja_environment(task: Task) -> jinja2.Environment:
    # TODO: Take device_type from host
    env = TEMPLAR.get_device_type_environment()
    return env

def template_generic(task: Task, template_name: str, params_spec: Dict = None, globals: Dict = None, extra_template_dirs: List[pathlib.Path] = None):
    print("Running")
    print(params_spec)
    env = get_jinja_environment(task=task)
    extend_jinja_env(env=env, extra_template_dirs=extra_template_dirs)
    template = env.get_template(name=template_name)

    params_dict = {}

    for key, expression in params_spec.items():
        print(key, expression)
        data = query_raw_params(data=task.host.data, expression=expression)
        params_dict[key] = data
    
    print(params_dict)

    return Result(host=task.host, result={"invocation": {'template_name': template_name, 'params_spec': params_spec}})


    