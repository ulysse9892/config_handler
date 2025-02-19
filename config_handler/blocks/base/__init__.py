from .utils import process_args, handle_import, handle_special
from typing import Union,List,Dict,Any,Callable

def create_wrapped_methods(methods:Union[List[Dict[str,Any]],Dict[str,Any]],
                           target: Union[type,Callable],
                           instantiator: bool=False,
                           glob_config:dict=None,
                           arg_key:str='args',
                           name_key:str='name',
                           use_key:str="use",
                           output_key:str='output'):
    if methods is None:
        return target

    if not isinstance(methods, list):
        methods = [methods]
    def wrapped_methods(*args, **kwargs):
        results = {}
        for m in methods:
            glob_config.update(results)
            if not handle_special(m.get(use_key,True),target, glob_config):
                continue
            method_and_args=process_args(m, target, glob_config)
            kwargs_to_use = kwargs.copy()
            kwargs_to_use.update(method_and_args.get(arg_key,{}))
            print(f"Calling {method_and_args[name_key]} with {args} and {kwargs_to_use}")
            result = method_and_args[name_key](*args, **kwargs_to_use)
            if instantiator:
                return result
            output = m.get(output_key)
            if output:
                results[output]=result
        return results
    return wrapped_methods

class ConfigMethodCaller:
    def __init__(self, config:Dict[str,Any],
                 glob_config:Dict[str,Any]=None,
                 local_key:str='local_args'):
        self.results = None
        local_args = process_args(config.get(local_key, {}), resource=glob_config,accessible=True)

        if glob_config:
            glob_config_local = glob_config.copy()
            glob_config_local.update(local_args)
        else:
            glob_config_local = local_args

        self.glob_config=glob_config_local
        self.config = config


    def call(self):
        if self.config.get('obj_name'):

            obj = handle_import(self.config['obj_name'])
            init_args = process_args(self.config.get('init_args', {}),resource=self.glob_config)

            # Attempt to create an instance of the obj
            if callable(obj):
                instance = obj(**init_args)
                print(f"CREATED OBJ {obj}({init_args})")
            else:
                instance = obj

            target = instance

            method = self.config.get('from')
            if method:
                from_method = create_wrapped_methods(method, instance,instantiator=True,glob_config=self.glob_config)
                target = from_method()
                print(f"INSTANTIATED FROM METHOD")
            else:
                print(f"NO INSTANTIATING METHOD")
        else:
            target=None

        methods=self.config.get('methods')

        execute_methods=create_wrapped_methods(methods,target,glob_config=self.glob_config)
        execute_methods()


class AllMethodsCaller:
    def __init__(self, config:Dict[str,Any],glob_key:str='$global'):
        self.results = None
        self.glob = process_args(config.pop(glob_key, {}),accessible=True)
        self.config = config

    def load(self,step:str):
        return ConfigMethodCaller(self.config[step],self.glob)

    def call(self,step:str):
        step_ready_to_execute = self.load(step)
        step_ready_to_execute.call()

