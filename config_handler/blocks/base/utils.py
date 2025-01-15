import os
from importlib import import_module
from config_handler.utils import load_configuration
from typing import List,Union,Dict,Any


def dict_replace_value(d:Dict[Any,Any],old,new):
    for k in d:
        if d[k]==old:
            d[k]=new
        elif isinstance(d[k], list) and len(d[k])==1 and d[k][0]==old:
            d[k] = [new]
    return d

def function_wrapper(function,function_args:Dict[str,Any]=None,*args, **kwargs):
    if function_args:
        kwargs.update(function_args)
    return function(*args, **kwargs)

def execute_actions(function=None,function_args:Dict[str,Any]=None,to_return:bool=True,actions:Union[List[Dict[str,Any]],Dict[str,Any]]=None,*args,**kwargs):
    result = None
    if actions:
        if isinstance(actions, dict):
            result={}
            for action in actions:
                action_to_do=actions[action]
                for r in result:
                    if "function_args" in action_to_do:
                        action_to_do["function_args"]=dict_replace_value(action_to_do["function_args"], r, result[r])
                    else:
                        action_to_do=dict_replace_value(action_to_do,r,result[r])
                result[action] = execute_actions(**action_to_do)
        else:
            for action in actions:
                result = execute_actions(**action)
    elif function is not None:
        result = function_wrapper(function, function_args, *args, **kwargs)
    if to_return:
        return result

def load_bound_method(cls,method:str,cls_args:Dict[str,Any]=None,*args, **kwargs):
    cls_instantiated=function_wrapper(cls,cls_args,*args,**kwargs)
    return getattr(cls_instantiated, method)

def execute_bound_method(cls,method:str,cls_args:Dict[str,Any]=None,*args, **kwargs):
    bound_method=load_bound_method(cls,method,cls_args)
    return bound_method(*args, **kwargs)


def dynamic_import(obj_path:str):
    module_name, obj_name = obj_path.rsplit('.', 1)
    module = import_module(module_name)
    method_keys = obj_name.split(":", 1)
    if len(method_keys) == 1:
        return getattr(module, obj_name)
    else:
        class_instance=getattr(module, method_keys[0])
        return getattr(class_instance, method_keys[1])

def get_nested_value(keys: List[str],dictionary:Dict[Any,Any]=None):
    if dictionary is None:
        return None
    value=dictionary.copy()
    for key in keys:
        value = value.get(key, {})
    return value

def is_global(value:str):
    return value.startswith("$global:")

def is_local(value:str):
    return value.startswith("$local:")

def is_path(value:str):
    return value.startswith("$path:")

def is_result(value:str):
    return value.startswith("$result:")

def is_import(value:str):
    return value.startswith("$import:")

def is_method(value:str):
    return value.startswith("$method:")

def is_config(value:str):
    return value.startswith("$config:")

def is_env(value:str):
    return value.startswith("$env:")



def handle_global(value:str,resource:Dict[str,Any]=None):
    global_key = value[8:]  # Remove the prefix
    if resource is not None:
        return resource.get(global_key)
    else:
        return globals().get(global_key)

def handle_result(value:str,resource:Dict[str,Any]=None):
    results_key = value[8:].split(".")  # Remove the prefix
    if resource is not None:
        result = resource.get(results_key[0])
    else:
        result = globals().get(results_key[0])
    if len(results_key)>1:
        keys=results_key[1:]
        return get_nested_value(keys,result)
    else:
        return result

def handle_env(value:str):
    env_key = value[5:]  # Remove the prefix
    return os.getenv(env_key)

def handle_path(value:str,resource:Dict[str,Any]=None):
    path_keys = value[6:].split(":",1)
    path_first=path_keys[0]
    if path_first in resource:
        base_path = resource[path_first]
    else:
        print(f"No path named {path_first}")
        return None
    os.makedirs(base_path, exist_ok=True)
    if len(path_keys)>1:
        path=os.path.join(base_path,path_keys[1])
    else:
        path=base_path
    return path

def handle_config(value:str,resource:Dict[str,Any]=None):
    config_key = value[8:]  # Remove the prefix
    if is_path(config_key):
        config_key=handle_path(config_key,resource)

    return load_configuration(config_key)

def handle_method(value:str,class_instance=None,resource:Dict[str,Any]=None):
    method_keys = value[8:].split(":", 1)
    if len(method_keys)>1:
        if resource is None:
            return value
        class_instance=resource[method_keys[0]]
        method_key=method_keys[1]
    else:
        method_key=method_keys[0]
    method = getattr(class_instance, method_key, None)
    if not method:
        print(f"Couldn't find {method_key} in {class_instance}")
        return value
    else:
        return method

def handle_import(value:str):
    import_key = value[8:]
    return dynamic_import(import_key)

def handle_special(name:Any,class_instance=None,resource:Dict[str,Any]=None):
    if not isinstance(name,str):
        return name
    if is_env(name):
        return handle_env(name)
    elif is_global(name):
        return handle_result(name,resource)
    elif is_import(name):
        return handle_import(name)
    elif is_method(name):
        return handle_method(name,class_instance,resource)
    elif is_result(name):
        return handle_result(name,resource)
    elif is_config(name):
        return handle_config(name,resource)
    elif is_path(name):
        return handle_path(name,resource)
    else:
        return name

def process_args(args:Dict[str,Any],class_instance=None,resource:Dict[str,Any]=None,accessible:bool=False):
    special_obj_key =  "obj_name"
    special_init_key =  "init_args"
    glob_key = "glob_arg"
    local_key = "local_args"

    if not resource:
        resource = {}

    def process_value(value:Any, key:str=None):
        if isinstance(value, str):
            result=handle_special(value,class_instance,resource)
            if accessible:
                resource[key] = result
            return result
        elif isinstance(value, list):
            return [process_value(v) for v in value]
        elif isinstance(value, dict):
            if not process_value(value.get("use",True)):
                return None
            if special_obj_key in value:
                if local_key in value:
                    local_args=process_args(value[local_key],class_instance,resource,accessible=True)
                    resource.update(local_args)
                obj = handle_special(value[special_obj_key],class_instance,resource)
                init_args = process_args(value.get(special_init_key, {}),class_instance,resource)
                if callable(obj):
                    if isinstance(init_args, list):
                        obj_initialized=obj(*init_args)
                    else:
                        obj_initialized=obj(**init_args)
                else:
                    obj_initialized = obj
                if key and (accessible or value.get(glob_key,False)):
                    resource[key]=obj_initialized
                return obj_initialized
            # Recursively process the nested dictionary
            return {k: process_value(v, k) for k, v in value.items()}
        else:
            return value

    if isinstance(args, list):
        processed_args=[]
        for value in args:
            processed_args.append(process_value(value))
    else:
        processed_args = {}
        for key, value in args.items():
            processed_args[key] = process_value(value,key)

    return processed_args


