import yaml # type: ignore
import os

def load_config(config_path: str = "config/config.yaml") -> dict:
    config_file_path = os.path.join(os.getcwd(), config_path)
    config = ''

    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)

    return config

if (__name__ == '__main__'):
    config = load_config()
    print(config)