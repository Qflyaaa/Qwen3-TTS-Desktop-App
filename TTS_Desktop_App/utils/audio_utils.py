# coding=utf-8
"""音频处理工具"""
import soundfile as sf
import numpy as np
from pathlib import Path

def get_audio_info(audio_path):
    """获取音频信息"""
    try:
        info = sf.info(audio_path)
        return {
            "duration": info.duration,
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "format": info.format
        }
    except Exception as e:
        return None

def validate_audio_file(audio_path):
    """验证音频文件"""
    if not Path(audio_path).exists():
        return False, "文件不存在"
    
    try:
        info = sf.info(audio_path)
        if info.duration < 1.0:
            return False, "音频时长太短（至少1秒）"
        if info.duration > 60.0:
            return False, "音频时长太长（最多60秒）"
        return True, "验证通过"
    except Exception as e:
        return False, f"音频文件格式错误: {e}"
