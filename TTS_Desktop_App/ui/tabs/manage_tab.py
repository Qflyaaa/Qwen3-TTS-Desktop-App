# coding=utf-8
"""文件管理标签页"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger
from utils.file_manager import FileManager
from utils.generation_params import GenerationParams
from ui.dialogs.params_viewer import ParamsViewer
from ui.dialogs.regenerate_dialog import RegenerateDialog
from ui.dialogs.batch_regenerate_dialog import BatchRegenerateDialog

class ManageTab:
    """文件管理标签页"""
    
    def __init__(self, parent, settings, params_regenerator=None):
        self.settings = settings
        self.file_manager = FileManager()
        self.params_manager = GenerationParams()
        self.params_regenerator = params_regenerator
        self.logger = get_logger()
        
        self.frame = tk.Frame(parent)
        self.setup_ui()
        self.refresh_all()
    
    def setup_ui(self):
        """设置UI"""
        # 创建Notebook用于分页
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 音色库标签页
        voices_frame = tk.Frame(notebook)
        notebook.add(voices_frame, text="音色库")
        self.setup_voices_tab(voices_frame)
        
        # 生成历史标签页
        outputs_frame = tk.Frame(notebook)
        notebook.add(outputs_frame, text="生成历史")
        self.setup_outputs_tab(outputs_frame)
        
        # 统计信息标签页
        stats_frame = tk.Frame(notebook)
        notebook.add(stats_frame, text="统计信息")
        self.setup_stats_tab(stats_frame)
    
    def setup_voices_tab(self, parent):
        """设置音色库标签页"""
        # 标题和按钮
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(header_frame, text="音色库", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="打开文件夹", command=self.open_voices_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_voices).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中", command=self.delete_selected_voice).pack(side=tk.LEFT, padx=5)
        
        # 列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview
        columns = ("name", "created", "usage", "size")
        self.voices_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.voices_tree.heading("name", text="音色名称")
        self.voices_tree.heading("created", text="创建时间")
        self.voices_tree.heading("usage", text="使用次数")
        self.voices_tree.heading("size", text="文件大小")
        
        self.voices_tree.column("name", width=150)
        self.voices_tree.column("created", width=150)
        self.voices_tree.column("usage", width=100)
        self.voices_tree.column("size", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.voices_tree.yview)
        self.voices_tree.configure(yscrollcommand=scrollbar.set)
        
        self.voices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_outputs_tab(self, parent):
        """设置生成历史标签页"""
        # 标题和按钮
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(header_frame, text="生成历史", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="打开文件夹", command=self.open_outputs_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_outputs).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="查看参数", command=self.view_params).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="重新生成", command=self.regenerate_from_params).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="批量复刻", command=self.batch_regenerate).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="播放选中", command=self.play_selected_output).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中", command=self.delete_selected_output).pack(side=tk.LEFT, padx=5)
        
        # 列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("name", "created", "size")
        self.outputs_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.outputs_tree.heading("name", text="文件名")
        self.outputs_tree.heading("created", text="创建时间")
        self.outputs_tree.heading("size", text="文件大小")
        
        self.outputs_tree.column("name", width=300)
        self.outputs_tree.column("created", width=150)
        self.outputs_tree.column("size", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.outputs_tree.yview)
        self.outputs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.outputs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_stats_tab(self, parent):
        """设置统计信息标签页"""
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 11),
            justify=tk.LEFT
        )
        self.stats_label.pack(anchor=tk.W)
        
        tk.Button(stats_frame, text="刷新统计", command=self.refresh_stats).pack(pady=10)
    
    def refresh_voices(self):
        """刷新音色列表"""
        # 清空列表
        for item in self.voices_tree.get_children():
            self.voices_tree.delete(item)
        
        # 添加音色
        voices = self.file_manager.list_voices()
        for voice in voices:
            self.voices_tree.insert("", tk.END, values=(
                voice["name"],
                voice["meta"].get("created_at", "未知"),
                voice["meta"].get("usage_count", 0),
                voice["file_size"]
            ))
    
    def refresh_outputs(self):
        """刷新生成历史"""
        # 清空列表
        for item in self.outputs_tree.get_children():
            self.outputs_tree.delete(item)
        
        # 添加输出文件
        outputs = self.file_manager.list_outputs(limit=100)
        for output in outputs:
            # 如果有参数文件，在文件名后添加标记
            name = output["name"]
            if output.get("has_params"):
                name = f"{name} [有参数]"
            
            self.outputs_tree.insert("", tk.END, values=(
                name,
                output["created"],
                f"{output['size']:.2f}MB"
            ), tags=(output["path"],))
    
    def refresh_stats(self):
        """刷新统计信息"""
        stats = self.file_manager.get_statistics()
        stats_text = f"""统计信息：

总音色数: {stats['total_voices']}
总生成数: {stats['total_outputs']}
占用空间: {stats['total_size_mb']:.2f} MB
"""
        self.stats_label.config(text=stats_text)
    
    def refresh_all(self):
        """刷新所有"""
        self.refresh_voices()
        self.refresh_outputs()
        self.refresh_stats()
    
    def delete_selected_voice(self):
        """删除选中的音色"""
        selection = self.voices_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的音色")
            return
        
        item = self.voices_tree.item(selection[0])
        voice_name = item["values"][0]
        
        if messagebox.askyesno("确认", f"确定要删除音色 '{voice_name}' 吗？"):
            if self.file_manager.delete_voice(voice_name):
                messagebox.showinfo("成功", "音色已删除")
                self.refresh_voices()
                self.refresh_stats()
            else:
                messagebox.showerror("错误", "删除失败")
    
    def play_selected_output(self):
        """播放选中的音频"""
        selection = self.outputs_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要播放的音频")
            return
        
        item = self.outputs_tree.item(selection[0])
        tags = item["tags"]
        if tags:
            audio_path = tags[0]
            # 使用系统默认程序打开
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(audio_path)
                else:  # Linux/Mac
                    subprocess.call(['xdg-open', audio_path])
            except Exception as e:
                messagebox.showerror("错误", f"无法播放音频: {e}")
    
    def open_voices_folder(self):
        """打开音色库文件夹"""
        voices_dir = self.file_manager.voices_dir
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(voices_dir))
            elif os.name == 'posix':  # Linux/Mac
                subprocess.call(['xdg-open' if os.name != 'darwin' else 'open', str(voices_dir)])
            else:
                messagebox.showinfo("提示", f"音色库路径: {voices_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def open_outputs_folder(self):
        """打开生成历史文件夹"""
        outputs_dir = self.file_manager.outputs_dir
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(outputs_dir))
            elif os.name == 'posix':  # Linux/Mac
                subprocess.call(['xdg-open' if os.name != 'darwin' else 'open', str(outputs_dir)])
            else:
                messagebox.showinfo("提示", f"生成历史路径: {outputs_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def view_params(self):
        """查看参数"""
        selection = self.outputs_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要查看参数的音频")
            return
        
        item = self.outputs_tree.item(selection[0])
        tags = item["tags"]
        if tags:
            audio_path = tags[0]
            params_file = self.params_manager.get_params_file(audio_path)
            if params_file:
                ParamsViewer(self.frame, params_file)
            else:
                messagebox.showinfo("提示", "该音频文件没有对应的参数文件")
    
    def regenerate_from_params(self):
        """根据参数重新生成"""
        if not self.params_regenerator:
            messagebox.showwarning("警告", "参数重新生成功能未初始化")
            return
        
        selection = self.outputs_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要重新生成的音频")
            return
        
        item = self.outputs_tree.item(selection[0])
        tags = item["tags"]
        if tags:
            audio_path = tags[0]
            params_file = self.params_manager.get_params_file(audio_path)
            if params_file:
                def on_success(output_path):
                    self.refresh_outputs()
                    self.refresh_stats()
                
                RegenerateDialog(self.frame, params_file, self.params_regenerator, on_success)
            else:
                messagebox.showinfo("提示", "该音频文件没有对应的参数文件")
    
    def batch_regenerate(self):
        """批量复刻"""
        if not self.params_regenerator:
            messagebox.showwarning("警告", "批量复刻功能未初始化")
            return
        
        def on_success(output_paths):
            self.refresh_outputs()
            self.refresh_stats()
        
        BatchRegenerateDialog(self.frame, self.params_regenerator, on_success)
    
    def delete_selected_output(self):
        """删除选中的输出"""
        selection = self.outputs_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的音频")
            return
        
        item = self.outputs_tree.item(selection[0])
        tags = item["tags"]
        if tags:
            audio_path = tags[0]
            if messagebox.askyesno("确认", f"确定要删除音频文件吗？"):
                try:
                    Path(audio_path).unlink()
                    # 同时删除参数文件
                    params_file = self.params_manager.get_params_file(audio_path)
                    if params_file and Path(params_file).exists():
                        Path(params_file).unlink()
                    messagebox.showinfo("成功", "音频已删除")
                    self.refresh_outputs()
                    self.refresh_stats()
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {e}")
