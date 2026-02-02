# coding=utf-8
"""音色设计标签页"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from ui.widgets.progress_bar import ProgressBar
from utils.logger import get_logger
from utils.text_utils import read_text_file, validate_text

class DesignTab:
    """音色设计标签页"""
    
    def __init__(self, parent, settings, model_loader, voice_designer):
        self.settings = settings
        self.model_loader = model_loader
        self.voice_designer = voice_designer
        self.logger = get_logger()
        
        self.frame = tk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title = tk.Label(
            self.frame,
            text="定制音色并朗读文本",
            font=("Arial", 12, "bold")
        )
        title.pack(pady=10)
        
        # 文本输入
        text_frame = tk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(text_frame, text="文本输入:").pack(anchor=tk.W)
        self.text_text = tk.Text(text_frame, height=8, wrap=tk.WORD)
        self.text_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text_btn_frame = tk.Frame(text_frame)
        text_btn_frame.pack(fill=tk.X)
        tk.Button(text_btn_frame, text="从文件加载", command=self.load_text_file).pack(side=tk.LEFT, padx=5)
        tk.Button(text_btn_frame, text="清空", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # 音色描述
        instruct_frame = tk.Frame(self.frame)
        instruct_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(instruct_frame, text="音色描述:").pack(anchor=tk.W)
        self.instruct_text = tk.Text(instruct_frame, height=4, wrap=tk.WORD)
        self.instruct_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        instruct_btn_frame = tk.Frame(instruct_frame)
        instruct_btn_frame.pack(fill=tk.X)
        tk.Button(instruct_btn_frame, text="从文件加载", command=self.load_instruct_file).pack(side=tk.LEFT, padx=5)
        tk.Button(instruct_btn_frame, text="预设描述", command=self.show_presets).pack(side=tk.LEFT, padx=5)
        tk.Button(instruct_btn_frame, text="清空", command=self.clear_instruct).pack(side=tk.LEFT, padx=5)
        
        # 语言和输出目录
        options_frame = tk.Frame(self.frame)
        options_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(options_frame, text="语言:").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value="Chinese")
        language_combo = ttk.Combobox(options_frame, textvariable=self.language_var,
                                     values=["Chinese", "English", "Japanese", "Korean", "Auto"],
                                     state="readonly", width=15)
        language_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(options_frame, text="输出目录:").pack(side=tk.LEFT, padx=5)
        self.output_dir_var = tk.StringVar(value="data/outputs")
        output_entry = tk.Entry(options_frame, textvariable=self.output_dir_var, width=25)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(options_frame, text="浏览...", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # 按钮
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.generate_btn = tk.Button(
            btn_frame,
            text="生成语音",
            command=self.start_generate,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_bar = ProgressBar(self.frame)
        self.progress_bar.frame.pack(fill=tk.X, padx=20, pady=10)
    
    def load_text_file(self):
        """加载文本文件"""
        filename = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            text = read_text_file(filename)
            if text:
                self.text_text.delete(1.0, tk.END)
                self.text_text.insert(1.0, text)
                self.text_file_name = Path(filename).stem
            else:
                messagebox.showerror("错误", "无法读取文本文件")
    
    def clear_text(self):
        """清空文本"""
        self.text_text.delete(1.0, tk.END)
        self.text_file_name = None
    
    def load_instruct_file(self):
        """加载音色描述文件"""
        filename = filedialog.askopenfilename(
            title="选择音色描述文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            text = read_text_file(filename)
            if text:
                self.instruct_text.delete(1.0, tk.END)
                self.instruct_text.insert(1.0, text)
            else:
                messagebox.showerror("错误", "无法读取文件")
    
    def clear_instruct(self):
        """清空描述"""
        self.instruct_text.delete(1.0, tk.END)
    
    def show_presets(self):
        """显示预设描述"""
        presets = [
            "声音软软带着点笑意，语气亲昵又黏人，温柔贤淑的淑女女声",
            "体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显，营造出黏人、做作又刻意卖萌的听觉效果",
            "成熟稳重的男声，音调较低，语速适中，声音浑厚有力",
            "活泼开朗的女声，音调较高，语速较快，充满活力和朝气"
        ]
        
        # 创建选择窗口
        preset_window = tk.Toplevel(self.frame)
        preset_window.title("选择预设描述")
        preset_window.geometry("500x300")
        
        listbox = tk.Listbox(preset_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for preset in presets:
            listbox.insert(tk.END, preset)
        
        def apply_preset():
            selection = listbox.curselection()
            if selection:
                preset_text = listbox.get(selection[0])
                self.instruct_text.delete(1.0, tk.END)
                self.instruct_text.insert(1.0, preset_text)
                preset_window.destroy()
        
        tk.Button(preset_window, text="应用", command=apply_preset).pack(pady=5)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir_var.set(dirname)
    
    def start_generate(self):
        """开始生成"""
        # 验证输入
        text = self.text_text.get(1.0, tk.END).strip()
        is_valid, msg = validate_text(text)
        if not is_valid:
            messagebox.showerror("错误", msg)
            return
        
        instruct = self.instruct_text.get(1.0, tk.END).strip()
        if not instruct:
            messagebox.showerror("错误", "请输入音色描述")
            return
        
        language = self.language_var.get()
        output_dir = self.output_dir_var.get()
        
        # 禁用按钮
        self.generate_btn.config(state=tk.DISABLED)
        self.progress_bar.reset()
        
        # 在新线程中执行
        thread = threading.Thread(
            target=self._generate_voice,
            args=(text, instruct, language, output_dir),
            daemon=True
        )
        thread.start()
    
    def _generate_voice(self, text, instruct, language, output_dir):
        """生成语音（在后台线程中执行）"""
        try:
            def progress_callback(progress, message):
                self.progress_bar.update(progress, message)
            
            text_file_name = getattr(self, 'text_file_name', None)
            output_path = self.voice_designer.generate_voice_design(
                text=text,
                instruct=instruct,
                language=language,
                output_dir=output_dir,
                text_file_name=text_file_name,
                progress_callback=progress_callback
            )
            
            # 成功
            self.frame.after(0, lambda: messagebox.showinfo(
                "成功",
                f"语音生成成功！\n路径: {output_path}"
            ))
            self.frame.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
            
        except Exception as e:
            self.logger.error(f"生成语音失败: {e}")
            self.frame.after(0, lambda: messagebox.showerror("错误", f"生成语音失败:\n{str(e)}"))
            self.frame.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
