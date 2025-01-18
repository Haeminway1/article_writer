import os
import json

def load_check_settings(model_name, check_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model', model_name)
    check_list_path = os.path.join(model_dir, 'check_list.json')

    if not os.path.exists(check_list_path):
        return {}

    with open(check_list_path, 'r', encoding='utf-8') as f:
        all_settings = json.load(f)

    return all_settings.get(check_name, {})

def save_check_settings(model_name, check_name, settings):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'data', 'model', model_name)
    check_list_path = os.path.join(model_dir, 'check_list.json')

    if os.path.exists(check_list_path):
        with open(check_list_path, 'r', encoding='utf-8') as f:
            all_settings = json.load(f)
    else:
        all_settings = {}

    all_settings[check_name] = settings

    with open(check_list_path, 'w', encoding='utf-8') as f:
        json.dump(all_settings, f, ensure_ascii=False, indent=4)

def load_checks():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checks_dir = os.path.join(base_dir, 'page2_checks', 'scripts')
    return [f.replace('.py', '') for f in os.listdir(checks_dir) if f.endswith('.py')]
