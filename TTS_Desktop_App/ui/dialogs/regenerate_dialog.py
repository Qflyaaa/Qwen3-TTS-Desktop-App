# coding=utf-8
"""根据参数重新生成对话框"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.generation_params import GenerationParams

class RegenerateDialog:
    """根据参数重新生成对话框"""
    
    def __init__(self, parent, params_file_path, params_regenerator, on_success=None):
        self.parent = parent
        self.params_file_path = params_file_path
        self.params_regenerator = params_regenerator
        self.on_success = on_success
        self.params_manager = GenerationParams()
        
        self.window = tk.Toplevel(parent)
        self.window.title("根据参数重新生成")
        self.window.geometry("600x500")
        
        self.params = None
        self.setup_ui()
        self.load_params()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title = tk.Label(self.window, text="根据参数重新生成", font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        # 参数信息
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(info_frame, text="参数文件:", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(info_frame, text=Path(self.params_file_path).name, 
                font=("Arial", 9), fg="gray").pack(anchor=tk.W)
        
        # 文本编辑区域
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(text_frame, text="文本内容（可修改）:").pack(anchor=tk.W)
        self.text_text = scrolledtext.ScrolledText(text_frame, height=6, wrap=tk.WORD)
        self.text_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 语气/描述编辑区域（根据类型显示）
        self.instruct_frame = tk.Frame(self.window)
        self.instruct_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.instruct_label = tk.Label(self.instruct_frame, text="")
        self.instruct_label.pack(anchor=tk.W)
        self.instruct_text = scrolledtext.ScrolledText(self.instruct_frame, height=4, wrap=tk.WORD)
        self.instruct_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.regenerate_btn = tk.Button(
            btn_frame,
            text="重新生成",
            command=self.start_regenerate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.regenerate_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="取消", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = tk.Label(self.window, text="", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=20, pady=2)
    
    def load_params(self):
        """加载参数"""
        try:
            self.params = self.params_manager.load_params(self.params_file_path)
            gen_type = self.params.get('generation_type')
            
            if gen_type == 'voice_clone':
                vc_params = self.params.get('voice_clone', {})
                self.text_text.insert(1.0, vc_params.get('text', ''))
                if vc_params.get('instruct'):
                    self.instruct_label.config(text="语气控制（可修改）:")
                    self.instruct_text.insert(1.0, vc_params.get('instruct', ''))
                else:
                    self.instruct_frame.pack_forget()
            elif gen_type == 'voice_design':
                vd_params = self.params.get('voice_design', {})
                self.text_text.insert(1.0, vd_params.get('text', ''))
                self.instruct_label.config(text="音色描述（可修改）:")
                self.instruct_text.insert(1.0, vd_params.get('instruct', ''))
                
        except Exception as e:
            messagebox.showerror("错误", f"加载参数失败: {e}")
            self.window.destroy()
    
    def start_regenerate(self):
        """开始重新生成"""
        text = self.text_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showerror("错误", "文本不能为空")
            return
        
        instruct = None
        if self.instruct_text.winfo_viewable():
            instruct = self.instruct_text.get(1.0, tk.END).strip() or None
        
        # 禁用按钮
        self.regenerate_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_label.config(text="准备生成...")
        
        # 在新线程中执行
        thread = threading.Thread(
            target=self._regenerate,
            args=(text, instruct),
            daemon=True
        )
        thread.start()
    
    def _regenerate(self, text, instruct):
        """重新生成（在后台线程中执行）"""
        try:
            def progress_callback(progress, message):
                self.progress_var.set(progress)
                self.status_label.config(text=message)
                self.window.update_idletasks()
            
            output_path = self.params_regenerator.regenerate_from_params(
                self.params_file_path,
                modify_text=text,
                modify_instruct=instruct,
                progress_callback=progress_callback
            )
            
            # 成功
            self.window.after(0, lambda: messagebox.showinfo(
                "成功",
                f"重新生成成功！\n路径: {output_path}"
            ))
            self.window.after(0, lambda: self.regenerate_btn.config(state=tk.NORMAL))
            
            if self.on_success:
                self.window.after(0, lambda: self.on_success(output_path))
            
            self.window.after(0, lambda: self.window.destroy())
            
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("错误", f"重新生成失败:\n{str(e)}"))
            self.window.after(0, lambda: self.regenerate_btn.config(state=tk.NORMAL))
