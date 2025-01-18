import os
import json
import shutil

def load_model_list():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model')
    return [name for name in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, name)) and name != 'default_model']

def load_model_settings(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model', model_name)
    config_path = os.path.join(model_dir, 'config.json')
    check_list_path = os.path.join(model_dir, 'check_list.json')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The config file {config_path} does not exist.")
    if not os.path.exists(check_list_path):
        raise FileNotFoundError(f"The check list settings file {check_list_path} does not exist.")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    with open(check_list_path, 'r', encoding='utf-8') as f:
        check_list_settings = json.load(f)

    return {
        'config': config['model_config'],
        'prompts': config['prompts'],
        'check_list_settings': check_list_settings
    }

def save_model_settings(model_name, config=None, prompts=None, check_list_settings=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model', model_name)
    config_path = os.path.join(model_dir, 'config.json')
    check_list_path = os.path.join(model_dir, 'check_list.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if config is not None:
            data['model_config'].update(config)
        if prompts is not None:
            data['prompts'] = prompts
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    if check_list_settings is not None:
        with open(check_list_path, 'w', encoding='utf-8') as f:
            json.dump(check_list_settings, f, ensure_ascii=False, indent=4)

def add_new_model(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model')
    default_model_dir = os.path.join(model_dir, 'default_model')
    new_model_dir = os.path.join(model_dir, model_name)

    if not os.path.exists(new_model_dir):
        shutil.copytree(default_model_dir, new_model_dir)
        create_default_settings(new_model_dir)
    else:
        raise FileExistsError(f"The model directory {new_model_dir} already exists.")

def create_default_settings(model_dir):
    check_list_settings = {
        "char_count_check": {
            "min_length": 300,
            "max_length": 1500
        },
        "forbidden_words_check": {
            "forbidden_words": ["금지어1", "금지어2", "금지어3"]
        }
    }

    with open(os.path.join(model_dir, 'check_list.json'), 'w', encoding='utf-8') as f:
        json.dump(check_list_settings, f, ensure_ascii=False, indent=4)

def delete_model(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model', model_name)
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    else:
        raise FileNotFoundError(f"The model directory {model_dir} does not exist.")

def copy_model(source_model_name, new_model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model')
    source_model_dir = os.path.join(model_dir, source_model_name)
    new_model_dir = os.path.join(model_dir, new_model_name)

    if not os.path.exists(new_model_dir):
        shutil.copytree(source_model_dir, new_model_dir)
    else:
        raise FileExistsError(f"The model directory {new_model_dir} already exists.")

def rename_model(old_name, new_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model')
    old_model_dir = os.path.join(model_dir, old_name)
    new_model_dir = os.path.join(model_dir, new_name)

    if old_name == new_name:
        print(f"The old name and new name are the same: {old_name}. No renaming needed.")
        return

    if not os.path.exists(old_model_dir):
        raise FileNotFoundError(f"The model directory {old_model_dir} does not exist.")
    
    if os.path.exists(new_model_dir):
        raise FileExistsError(f"The model directory {new_model_dir} already exists.")
    
    os.rename(old_model_dir, new_model_dir)
    print(f"Model directory renamed from {old_model_dir} to {new_model_dir}.")

