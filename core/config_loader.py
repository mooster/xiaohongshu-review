"""配置加载器"""
import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")


def load_config(config_name: str) -> dict:
    """加载指定的审核配置文件"""
    path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_configs() -> list[dict]:
    """列出所有可用配置"""
    configs = []
    for f in os.listdir(CONFIG_DIR):
        if f.endswith('.json'):
            path = os.path.join(CONFIG_DIR, f)
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                configs.append({
                    "file": f.replace('.json', ''),
                    "brand": data["meta"]["brand"],
                    "direction": data["meta"]["direction"],
                    "label": f"{data['meta']['brand']} - {data['meta']['direction']}"
                })
    return configs
