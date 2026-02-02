# coding=utf-8
"""语音克隆标签页"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from ui.widgets.progress_bar import ProgressBar
from utils.logger import get_logger
from utils.audio_utils import validate_audio_file
from utils.text_utils import read_text_file, validate_text

class CloneTab:
    """语音克隆标签页"""
    
    def __init__(self, parent, settings, model_loader, voice_clone_manager):
        self.settings = settings
        self.model_loader = model_loader
        self.voice_clone_manager = voice_clone_manager
        self.logger = get_logger()
        
        self.frame = tk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title = tk.Label(
            self.frame,
            text="语音克隆并保存音色特征",
            font=("Arial", 12, "bold")
        )
        title.pack(pady=10)
        
        # 参考音频选择
        audio_frame = tk.Frame(self.frame)
        audio_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(audio_frame, text="参考音频:").pack(side=tk.LEFT, padx=5)
        self.audio_path_var = tk.StringVar()
        audio_entry = tk.Entry(audio_frame, textvariable=self.audio_path_var, width=50)
        audio_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(audio_frame, text="浏览...", command=self.browse_audio).pack(side=tk.LEFT, padx=5)
        
        # 参考文本输入
        text_frame = tk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(text_frame, text="参考文本:").pack(anchor=tk.W)
        self.text_text = tk.Text(text_frame, height=5, wrap=tk.WORD)
        self.text_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text_btn_frame = tk.Frame(text_frame)
        text_btn_frame.pack(fill=tk.X)
        tk.Button(text_btn_frame, text="从文件加载", command=self.load_text_file).pack(side=tk.LEFT, padx=5)
        tk.Button(text_btn_frame, text="清空", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # 音色名称
        name_frame = tk.Frame(self.frame)
        name_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(name_frame, text="音色名称:").pack(side=tk.LEFT, padx=5)
        self.voice_name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.voice_name_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # 模式选择
        mode_frame = tk.Frame(self.frame)
        mode_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.mode_var = tk.StringVar(value="full")
        tk.Radiobutton(
            mode_frame,
            text="完整模式（推荐）",
            variable=self.mode_var,
            value="full"
        ).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(
            mode_frame,
            text="仅X-Vector模式",
            variable=self.mode_var,
            value="x_vector"
        ).pack(side=tk.LEFT, padx=10)
        
        # 按钮
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.extract_btn = tk.Button(
            btn_frame,
            text="开始提取特征",
            command=self.start_extract,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_bar = ProgressBar(self.frame)
        self.progress_bar.frame.pack(fill=tk.X, padx=20, pady=10)
    
    def browse_audio(self):
        """浏览音频文件"""
        filename = filedialog.askopenfilename(
            title="选择参考音频",
            filetypes=[("音频文件", "*.wav *.mp3 *.flac"), ("所有文件", "*.*")]
        )
        if filename:
            self.audio_path_var.set(filename)
            # 自动提取文件名作为音色名称
            if not self.voice_name_var.get():
                name = Path(filename).stem
                self.voice_name_var.set(name)
    
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
            else:
                messagebox.showerror("错误", "无法读取文本文件")
    
    def clear_text(self):
        """清空文本"""
        self.text_text.delete(1.0, tk.END)
    
    def start_extract(self):
        """开始提取特征"""
        # 验证输入
        audio_path = self.audio_path_var.get().strip()
        if not audio_path:
            messagebox.showerror("错误", "请选择参考音频文件")
            return
        
        is_valid, msg = validate_audio_file(audio_path)
        if not is_valid:
            messagebox.showerror("错误", msg)
            return
        
        text = self.text_text.get(1.0, tk.END).strip()
        is_valid, msg = validate_text(text)
        if not is_valid:
            messagebox.showerror("错误", msg)
            return
        
        voice_name = self.voice_name_var.get().strip()
        if not voice_name:
            messagebox.showerror("错误", "请输入音色名称")
            return
        
        # 禁用按钮
        self.extract_btn.config(state=tk.DISABLED)
        self.progress_bar.reset()
        
        # 在新线程中执行
        x_vector_only = (self.mode_var.get() == "x_vector")
        thread = threading.Thread(
            target=self._extract_features,
            args=(audio_path, text, voice_name, x_vector_only),
            daemon=True
        )
        thread.start()
    
    def _extract_features(self, audio_path, text, voice_name, x_vector_only):
        """提取特征（在后台线程中执行）"""
        try:
            def progress_callback(progress, message):
                self.progress_bar.update(progress, message)
            
            output_path = self.voice_clone_manager.extract_features(
                ref_audio_path=audio_path,
                ref_text=text,
                voice_name=voice_name,
                x_vector_only=x_vector_only,
                progress_callback=progress_callback
            )
            
            # 成功
            self.frame.after(0, lambda: messagebox.showinfo(
                "成功",
                f"音色特征已保存！\n路径: {output_path}"
            ))
            self.frame.after(0, lambda: self.extract_btn.config(state=tk.NORMAL))
            
        except Exception as e:
            self.logger.error(f"提取特征失败: {e}")
            self.frame.after(0, lambda: messagebox.showerror("错误", f"提取特征失败:\n{str(e)}"))
            self.frame.after(0, lambda: self.extract_btn.config(state=tk.NORMAL))
