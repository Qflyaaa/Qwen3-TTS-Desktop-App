# coding=utf-8
"""日志系统"""
import logging
import os
from datetime import datetime
from pathlib import Path

_logger = None

def setup_logger(name="TTS_App", level=logging.INFO):
    """设置日志系统"""
    global _logger
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志文件名（按日期）
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 创建logger
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    
    # 避免重复添加handler
    if not _logger.handlers:
        _logger.addHandler(file_handler)
        _logger.addHandler(console_handler)
    
    return _logger

def get_logger(name="TTS_App"):
    """获取logger实例"""
    global _logger
    if _logger is None:
        return setup_logger(name)
    return _logger
