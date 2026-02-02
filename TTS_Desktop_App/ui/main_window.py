# coding=utf-8
"""主窗口"""
import tkinter as tk
from tkinter import ttk, messagebox
import torch
from core.model_loader import ModelLoader
from core.voice_clone_manager import VoiceCloneManager
from core.voice_generator import VoiceGenerator
from core.voice_designer import VoiceDesigner
from core.params_regenerator import ParamsRegenerator
from ui.tabs.clone_tab import CloneTab
from ui.tabs.generate_tab import GenerateTab
from ui.tabs.design_tab import DesignTab
from ui.tabs.manage_tab import ManageTab
from utils.logger import get_logger

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger()
        
        # 初始化核心组件
        self.model_loader = ModelLoader()
        self.voice_clone_manager = VoiceCloneManager(self.model_loader)
        self.voice_generator = VoiceGenerator(self.model_loader)
        self.voice_designer = VoiceDesigner(self.model_loader)
        self.params_regenerator = ParamsRegenerator(
            self.model_loader,
            self.voice_generator,
            self.voice_designer
        )
        
        self.setup_window()
        self.create_menu()
        self.create_tabs()
        self.create_status_bar()
        
        # 更新状态栏
        self.update_status("就绪")
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("Qwen3-TTS 语音合成工具")
        
        width = self.settings.get("ui.window_width", 1000)
        height = self.settings.get("ui.window_height", 700)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 600)
        
        # 居中显示
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.on_exit)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="偏好设置", command=self.open_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_tabs(self):
        """创建标签页"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页
        self.clone_tab = CloneTab(
            notebook, 
            self.settings,
            self.model_loader,
            self.voice_clone_manager
        )
        self.generate_tab = GenerateTab(
            notebook,
            self.settings,
            self.model_loader,
            self.voice_generator
        )
        self.design_tab = DesignTab(
            notebook,
            self.settings,
            self.model_loader,
            self.voice_designer
        )
        self.manage_tab = ManageTab(
            notebook,
            self.settings,
            self.params_regenerator
        )
        
        notebook.add(self.clone_tab.frame, text="语音克隆")
        notebook.add(self.generate_tab.frame, text="文本朗读")
        notebook.add(self.design_tab.frame, text="音色设计")
        notebook.add(self.manage_tab.frame, text="文件管理")
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """更新状态栏"""
        # 获取GPU信息
        gpu_info = "GPU: "
        if torch.cuda.is_available():
            gpu_info += f"CUDA ({torch.cuda.get_device_name(0)})"
        else:
            gpu_info += "CPU"
        
        # 获取模型状态
        model_status = "模型: "
        if self.model_loader._base_model is not None:
            model_status += "已加载"
        else:
            model_status += "未加载"
        
        status_text = f"{message} | {gpu_info} | {model_status}"
        self.status_bar.config(text=status_text)
    
    def open_settings(self):
        """打开设置对话框"""
        messagebox.showinfo("设置", "设置功能开发中...")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """Qwen3-TTS 语音合成工具

版本: 1.0.0

功能:
• 语音克隆并保存音色特征
• 加载音色特征并朗读文本
• 定制音色并朗读文本
• 文件管理和统计

基于 Qwen3-TTS 模型
"""
        messagebox.showinfo("关于", about_text)
    
    def on_exit(self):
        """退出应用"""
        self.logger.info("应用退出")
        # 卸载模型释放内存
        self.model_loader.unload_models()
        self.root.quit()
