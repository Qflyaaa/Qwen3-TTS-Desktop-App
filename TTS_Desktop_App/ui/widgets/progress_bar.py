# coding=utf-8
"""进度条组件"""
import tkinter as tk
from tkinter import ttk

class ProgressBar:
    """进度条组件"""
    
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = tk.Label(
            self.frame,
            text="就绪",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def update(self, progress, message=""):
        """更新进度"""
        self.progress_var.set(progress)
        if message:
            self.status_label.config(text=message)
        self.frame.update_idletasks()
    
    def reset(self):
        """重置进度条"""
        self.progress_var.set(0)
        self.status_label.config(text="就绪")
