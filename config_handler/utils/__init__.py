import yaml
from dotenv import load_dotenv
from os.path import exists
from typing import Union

def load_configuration(path:str,string:bool=False):
    if exists(path):
        # Load and return the configuration from the YAML file
        with open(path, 'r',encoding='utf-8') as file:
            if string:
                return file.read()
            else:
                return yaml.safe_load(file)
    else:
        return None

def update_configuration(data:dict,path:str,on_change:Union[bool,dict]=False):
    if on_change:
        if isinstance(on_change,dict):
            data_old=on_change
        else:
            data_old=load_configuration(path)
    else:
        data_old=None
    if data_old!=data:
        with open(path, 'w',encoding='utf-8') as file:
            yaml.dump(data, file)



def placeholder(value):
    return value

def config_loader(file=None):

    if file is None:
        return None
    else:
        if isinstance(file,str):
            config = load_configuration(file)
        else:
            config = yaml.safe_load(file)

    if "env_path" in config:
        load_dotenv(dotenv_path=config["env_path"])


    return config