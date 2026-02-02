# coding=utf-8
"""文本处理工具"""
from pathlib import Path

def read_text_file(file_path):
    """读取文本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return None

def validate_text(text):
    """验证文本"""
    if not text or not text.strip():
        return False, "文本不能为空"
    if len(text) > 5000:
        return False, "文本过长（最多5000字符）"
    return True, "验证通过"
