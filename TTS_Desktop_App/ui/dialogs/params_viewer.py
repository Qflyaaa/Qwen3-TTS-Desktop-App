# coding=utf-8
"""参数查看对话框"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.generation_params import GenerationParams

class ParamsViewer:
    """参数查看对话框"""
    
    def __init__(self, parent, params_file_path):
        self.parent = parent
        self.params_file_path = params_file_path
        self.params_manager = GenerationParams()
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"生成参数详情 - {Path(params_file_path).name}")
        self.window.geometry("700x600")
        
        self.setup_ui()
        self.load_params()
    
    def setup_ui(self):
        """设置UI"""
        # 创建Notebook
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 详细信息标签页
        detail_frame = tk.Frame(notebook)
        notebook.add(detail_frame, text="详细信息")
        self.setup_detail_tab(detail_frame)
        
        # JSON原始数据标签页
        json_frame = tk.Frame(notebook)
        notebook.add(json_frame, text="JSON数据")
        self.setup_json_tab(json_frame)
        
        # 按钮
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def setup_detail_tab(self, parent):
        """设置详细信息标签页"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.detail_frame = scrollable_frame
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_json_tab(self, parent):
        """设置JSON数据标签页"""
        self.json_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Consolas", 10))
        self.json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_params(self):
        """加载参数"""
        try:
            params = self.params_manager.load_params(self.params_file_path)
            
            # 显示详细信息
            self.show_details(params)
            
            # 显示JSON
            json_str = json.dumps(params, ensure_ascii=False, indent=2)
            self.json_text.insert(1.0, json_str)
            self.json_text.config(state=tk.DISABLED)
            
        except Exception as e:
            error_label = tk.Label(self.detail_frame, text=f"加载参数失败: {e}", fg="red")
            error_label.pack(pady=10)
    
    def show_details(self, params):
        """显示详细信息"""
        row = 0
        
        # 基本信息
        self.add_label(self.detail_frame, "生成类型:", params.get('generation_type', '未知'), row)
        row += 1
        self.add_label(self.detail_frame, "生成时间:", params.get('timestamp', '未知'), row)
        row += 1
        self.add_label(self.detail_frame, "输出文件:", params.get('output_audio', '未知'), row)
        row += 1
        
        # 分隔线
        ttk.Separator(self.detail_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1
        
        # 根据类型显示不同内容
        gen_type = params.get('generation_type')
        
        if gen_type == 'voice_clone':
            self.show_voice_clone_details(params.get('voice_clone', {}), row)
            row += 10
        elif gen_type == 'voice_design':
            self.show_voice_design_details(params.get('voice_design', {}), row)
            row += 8
        
        # 模型信息
        ttk.Separator(self.detail_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1
        
        model_info = params.get('model', {})
        self.add_label(self.detail_frame, "模型类型:", model_info.get('model_type', '未知'), row)
        row += 1
        self.add_label(self.detail_frame, "设备:", model_info.get('device', '未知'), row)
        row += 1
        self.add_label(self.detail_frame, "FlashAttention:", "启用" if model_info.get('use_flash_attention') else "禁用", row)
        row += 1
    
    def show_voice_clone_details(self, vc_params, start_row):
        """显示语音克隆详细信息"""
        row = start_row
        
        tk.Label(self.detail_frame, text="音色信息", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1
        
        self.add_label(self.detail_frame, "音色名称:", vc_params.get('voice_name', '未知'), row)
        row += 1
        self.add_label(self.detail_frame, "特征文件:", vc_params.get('voice_features_path', '未知'), row)
        row += 1
        
        tk.Label(self.detail_frame, text="文本内容", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1
        
        text = vc_params.get('text', '')
        text_label = tk.Label(self.detail_frame, text=text[:200] + ('...' if len(text) > 200 else ''), 
                             wraplength=600, justify=tk.LEFT)
        text_label.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1
        
        if vc_params.get('instruct'):
            tk.Label(self.detail_frame, text="语气控制", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
            row += 1
            
            instruct = vc_params.get('instruct', '')
            instruct_label = tk.Label(self.detail_frame, text=instruct, 
                                     wraplength=600, justify=tk.LEFT)
            instruct_label.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
            row += 1
        
        self.add_label(self.detail_frame, "语言:", vc_params.get('language', 'Chinese'), row)
        row += 1
    
    def show_voice_design_details(self, vd_params, start_row):
        """显示音色设计详细信息"""
        row = start_row
        
        tk.Label(self.detail_frame, text="文本内容", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1
        
        text = vd_params.get('text', '')
        text_label = tk.Label(self.detail_frame, text=text[:200] + ('...' if len(text) > 200 else ''), 
                             wraplength=600, justify=tk.LEFT)
        text_label.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1
        
        tk.Label(self.detail_frame, text="音色描述", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', pady=5)
        row += 1
        
        instruct = vd_params.get('instruct', '')
        instruct_label = tk.Label(self.detail_frame, text=instruct, 
                                 wraplength=600, justify=tk.LEFT)
        instruct_label.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        row += 1
        
        self.add_label(self.detail_frame, "语言:", vd_params.get('language', 'Chinese'), row)
        row += 1
    
    def add_label(self, parent, label_text, value_text, row):
        """添加标签行"""
        tk.Label(parent, text=label_text, font=("Arial", 9)).grid(row=row, column=0, sticky='w', padx=10, pady=2)
        tk.Label(parent, text=str(value_text), font=("Arial", 9)).grid(row=row, column=1, sticky='w', padx=10, pady=2)
