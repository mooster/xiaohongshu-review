"""配置加载器"""
import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")

REQUIRED_KEYS = {
    "meta": ["brand", "direction", "platform"],
    "hard_rules": ["word_count", "titles", "hashtags", "forbidden_words", "structure"],
}


def _validate_config(data: dict, file_path: str):
    """校验配置文件必要字段"""
    for section, keys in REQUIRED_KEYS.items():
        if section not in data:
            raise ValueError(f"配置文件缺少 '{section}' 段: {file_path}")
        for key in keys:
            if key not in data[section]:
                raise ValueError(f"配置文件 {section} 缺少 '{key}': {file_path}")

    hr = data["hard_rules"]
    if "paragraphs" not in hr["structure"]:
        raise ValueError(f"配置文件 structure 缺少 'paragraphs': {file_path}")
    if "required" not in hr["hashtags"]:
        raise ValueError(f"配置文件 hashtags 缺少 'required': {file_path}")


def load_config(config_name: str) -> dict:
    """加载指定的审核配置文件"""
    path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"配置文件不存在: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件 JSON 格式错误: {path}\n{e}")

    _validate_config(data, path)
    return data


def list_configs() -> list[dict]:
    """列出所有可用配置"""
    configs = []
    if not os.path.isdir(CONFIG_DIR):
        return configs
    for f in sorted(os.listdir(CONFIG_DIR)):
        if f.endswith('.json') and not f.startswith('_'):
            path = os.path.join(CONFIG_DIR, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                    meta = data.get("meta", {})
                    did = meta.get("direction_id", "")
                    num = did.replace("direction_", "方向") if did.startswith("direction_") else ""
                    configs.append({
                        "file": f.replace('.json', ''),
                        "brand": meta.get("brand", "未知"),
                        "direction": meta.get("direction", "未知"),
                        "label": f"{num} · {meta.get('direction', '未知')}" if num else f"{meta.get('brand', '未知')} - {meta.get('direction', '未知')}",
                    })
            except (json.JSONDecodeError, KeyError):
                continue
    return configs
