# coding=utf-8
"""常量定义"""

# 项目根目录
import os
from pathlib import Path

# TTS_Desktop_App 目录
PROJECT_ROOT = Path(__file__).parent.parent
# 工作空间根目录（TTS_workspace）
WORKSPACE_ROOT = PROJECT_ROOT.parent

# 默认路径
DEFAULT_PATHS = {
    "voices": "data/voices",
    "audios": "data/audios",
    "texts": "data/texts",
    "outputs": "data/outputs",
    "logs": "data/logs"
}

# 默认模型路径（相对于工作空间）
DEFAULT_MODELS = {
    "base": str(WORKSPACE_ROOT / "Qwen3-TTS" / "Qwen3-TTS-12Hz-1.7B-Base"),
    "voice_design": str(WORKSPACE_ROOT / "Qwen3-TTS" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign")
}

# 支持的语言
SUPPORTED_LANGUAGES = ["Chinese", "English", "Japanese", "Korean", "Auto"]

# 窗口默认大小
DEFAULT_WINDOW_SIZE = {
    "width": 1000,
    "height": 700
}
