# coding=utf-8
"""
主程序入口
"""
import tkinter as tk
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_settings
from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """主函数"""
    # 初始化日志
    logger = setup_logger()
    logger.info("="*60)
    logger.info("应用启动")
    logger.info("="*60)
    
    # 加载配置
    try:
        settings = load_settings()
        logger.info("配置加载成功")
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        settings = load_settings()  # 使用默认配置
    
    # 创建主窗口
    try:
        root = tk.Tk()
        app = MainWindow(root, settings)
        
        # 运行应用
        root.mainloop()
        
        logger.info("应用退出")
    except Exception as e:
        logger.error(f"应用运行错误: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
