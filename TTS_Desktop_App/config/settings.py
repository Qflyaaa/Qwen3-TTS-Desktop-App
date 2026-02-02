# coding=utf-8
"""配置管理"""
import json
from pathlib import Path
from .constants import DEFAULT_PATHS, DEFAULT_MODELS, DEFAULT_WINDOW_SIZE

class Settings:
    """设置管理类"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "config" / "app_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.default_config = {
            "paths": DEFAULT_PATHS.copy(),
            "models": DEFAULT_MODELS.copy(),
            "defaults": {
                "language": "Chinese",
                "device": "cuda:0",
                "use_flash_attention": True
            },
            "ui": DEFAULT_WINDOW_SIZE.copy()
        }
        
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并默认配置和用户配置
                    config = self.default_config.copy()
                    config.update(user_config)
                    return config
            except Exception as e:
                print(f"加载配置失败: {e}，使用默认配置")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key, value):
        """设置配置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

def load_settings():
    """加载设置实例"""
    return Settings()
