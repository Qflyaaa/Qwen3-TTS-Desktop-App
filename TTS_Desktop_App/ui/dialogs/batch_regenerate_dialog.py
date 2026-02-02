# coding=utf-8
"""批量重新生成对话框"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import threading
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.generation_params import GenerationParams

class BatchRegenerateDialog:
    """批量重新生成对话框"""
    
    def __init__(self, parent, params_regenerator, on_success=None):
        self.parent = parent
        self.params_regenerator = params_regenerator
        self.on_success = on_success
        self.params_manager = GenerationParams()
        
        self.window = tk.Toplevel(parent)
        self.window.title("批量重新生成")
        self.window.geometry("700x600")
        
        self.params_files = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title = tk.Label(self.window, text="批量根据参数重新生成", font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        # 文件选择区域
        file_frame = tk.Frame(self.window)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(file_frame, text="参数文件列表:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # 文件列表
        list_frame = tk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 按钮
        btn_frame1 = tk.Frame(file_frame)
        btn_frame1.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame1, text="添加文件", command=self.add_files).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="添加文件夹", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="移除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="清空列表", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        
        # 选项
        options_frame = tk.Frame(self.window)
        options_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.modify_text_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="批量修改文本", 
                      variable=self.modify_text_var,
                      command=self.toggle_text_edit).pack(side=tk.LEFT, padx=10)
        
        
        # 文本编辑区域（初始隐藏）
        self.text_edit_frame = tk.Frame(self.window)
        # 不pack，等待用户勾选后再显示
        
        # 操作按钮
        self.action_frame = tk.Frame(self.window)
        self.action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_btn = tk.Button(
            self.action_frame,
            text="开始批量生成",
            command=self.start_batch_regenerate,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.action_frame, text="关闭", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = tk.Label(self.window, text="", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=20, pady=2)
    
    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择参数文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        for file in files:
            if file not in self.params_files:
                self.params_files.append(file)
                self.file_listbox.insert(tk.END, Path(file).name)
    
    def add_folder(self):
        """添加文件夹中的所有参数文件"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            folder_path = Path(folder)
            json_files = list(folder_path.glob("*.json"))
            for json_file in json_files:
                file_str = str(json_file)
                if file_str not in self.params_files:
                    self.params_files.append(file_str)
                    self.file_listbox.insert(tk.END, json_file.name)
    
    def remove_selected(self):
        """移除选中的文件"""
        selections = self.file_listbox.curselection()
        for index in reversed(selections):
            self.file_listbox.delete(index)
            del self.params_files[index]
    
    def clear_list(self):
        """清空列表"""
        self.file_listbox.delete(0, tk.END)
        self.params_files.clear()
    
    def toggle_text_edit(self):
        """切换文本编辑区域"""
        if self.modify_text_var.get():
            if not hasattr(self, 'text_edit_text'):
                tk.Label(self.text_edit_frame, text="新文本内容（将应用到所有文件）:").pack(anchor=tk.W, padx=10, pady=5)
                self.text_edit_text = scrolledtext.ScrolledText(self.text_edit_frame, height=4, wrap=tk.WORD)
                self.text_edit_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            # 在操作按钮之前插入
            self.text_edit_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5, before=self.action_frame)
        else:
            self.text_edit_frame.pack_forget()
    
    def start_batch_regenerate(self):
        """开始批量生成"""
        if not self.params_files:
            messagebox.showwarning("警告", "请先添加参数文件")
            return
        
        # 禁用按钮
        self.start_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_label.config(text="准备批量生成...")
        
        # 获取修改后的文本
        modify_text = None
        if self.modify_text_var.get() and hasattr(self, 'text_edit_text'):
            modify_text = self.text_edit_text.get(1.0, tk.END).strip()
            if not modify_text:
                modify_text = None
        
        # 在新线程中执行
        thread = threading.Thread(
            target=self._batch_regenerate,
            args=(modify_text,),
            daemon=True
        )
        thread.start()
    
    def _batch_regenerate(self, modify_text):
        """批量重新生成（在后台线程中执行）"""
        try:
            modify_texts = [modify_text] * len(self.params_files) if modify_text else None
            
            def progress_callback(total, current, message):
                progress = (current / total) * 100 if total > 0 else 0
                self.progress_var.set(progress)
                self.status_label.config(text=message)
                self.window.update_idletasks()
            
            output_paths = self.params_regenerator.batch_regenerate(
                self.params_files,
                modify_texts=modify_texts,
                progress_callback=progress_callback
            )
            
            # 统计结果
            success_count = sum(1 for p in output_paths if p is not None)
            fail_count = len(output_paths) - success_count
            
            # 成功
            self.window.after(0, lambda: messagebox.showinfo(
                "批量生成完成",
                f"成功: {success_count} 个\n失败: {fail_count} 个"
            ))
            self.window.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            
            if self.on_success:
                self.window.after(0, lambda: self.on_success(output_paths))
            
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("错误", f"批量生成失败:\n{str(e)}"))
            self.window.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
