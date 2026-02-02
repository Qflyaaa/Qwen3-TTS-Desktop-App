# coding=utf-8
"""模型加载器（单例模式）"""
import torch
import sys
from pathlib import Path

# 添加工作空间路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "Qwen3-TTS"))

from qwen_tts import Qwen3TTSModel

class ModelLoader:
    """模型加载器（单例模式）"""
    _instance = None
    _base_model = None
    _voice_design_model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.base_model_path = None
            self.voice_design_model_path = None
            self.device = "cuda:0"
            self.use_flash_attention = True
    
    def get_base_model(self, model_path=None, device=None, use_flash_attention=None):
        """获取Base模型"""
        if model_path is None:
            from config.constants import DEFAULT_MODELS
            model_path = DEFAULT_MODELS["base"]
        
        if device is None:
            device = self.device
        
        if use_flash_attention is None:
            use_flash_attention = self.use_flash_attention
        
        # 如果模型已加载且路径相同，直接返回
        if (self._base_model is not None and 
            self.base_model_path == model_path and
            self.device == device):
            return self._base_model
        
        # 检测设备
        if device.startswith("cuda") and not torch.cuda.is_available():
            print("⚠ CUDA 不可用，切换到 CPU")
            device = "cpu"
        
        # 检测 FlashAttention
        attn_implementation = None
        if use_flash_attention and device != "cpu":
            try:
                import flash_attn
                attn_implementation = "flash_attention_2"
                print("✓ 使用 FlashAttention 2")
            except ImportError:
                print("⚠ FlashAttention 未安装，使用默认实现")
                attn_implementation = "eager"
        else:
            attn_implementation = "eager"
        
        # 设置 dtype
        dtype = torch.bfloat16 if device != "cpu" else torch.float32
        
        # 确保路径是绝对路径且存在
        model_path_obj = Path(model_path).resolve()
        if not model_path_obj.exists():
            raise FileNotFoundError(f"模型路径不存在: {model_path_obj}")
        
        # 转换为字符串，使用正斜杠（HuggingFace 可能更兼容）
        model_path_str = str(model_path_obj).replace('\\', '/')
        
        print(f"正在加载Base模型: {model_path_str}")
        try:
            self._base_model = Qwen3TTSModel.from_pretrained(
                model_path_str,
                device_map=device,
                dtype=dtype,
                attn_implementation=attn_implementation,
            )
            self.base_model_path = model_path
            self.device = device
            print("✓ Base模型加载成功")
            return self._base_model
        except Exception as e:
            print(f"✗ Base模型加载失败: {e}")
            raise
    
    def get_voice_design_model(self, model_path=None, device=None, use_flash_attention=None):
        """获取VoiceDesign模型"""
        if model_path is None:
            from config.constants import DEFAULT_MODELS
            model_path = DEFAULT_MODELS["voice_design"]
        
        if device is None:
            device = self.device
        
        if use_flash_attention is None:
            use_flash_attention = self.use_flash_attention
        
        # 如果模型已加载且路径相同，直接返回
        if (self._voice_design_model is not None and 
            self.voice_design_model_path == model_path and
            self.device == device):
            return self._voice_design_model
        
        # 检测设备
        if device.startswith("cuda") and not torch.cuda.is_available():
            print("⚠ CUDA 不可用，切换到 CPU")
            device = "cpu"
        
        # 检测 FlashAttention
        attn_implementation = None
        if use_flash_attention and device != "cpu":
            try:
                import flash_attn
                attn_implementation = "flash_attention_2"
            except ImportError:
                attn_implementation = "eager"
        else:
            attn_implementation = "eager"
        
        # 设置 dtype
        dtype = torch.bfloat16 if device != "cpu" else torch.float32
        
        # 确保路径是绝对路径且存在
        model_path_obj = Path(model_path).resolve()
        if not model_path_obj.exists():
            raise FileNotFoundError(f"模型路径不存在: {model_path_obj}")
        
        # 转换为字符串，使用正斜杠（HuggingFace 可能更兼容）
        model_path_str = str(model_path_obj).replace('\\', '/')
        
        print(f"正在加载VoiceDesign模型: {model_path_str}")
        try:
            self._voice_design_model = Qwen3TTSModel.from_pretrained(
                model_path_str,
                device_map=device,
                dtype=dtype,
                attn_implementation=attn_implementation,
            )
            self.voice_design_model_path = model_path
            print("✓ VoiceDesign模型加载成功")
            return self._voice_design_model
        except Exception as e:
            print(f"✗ VoiceDesign模型加载失败: {e}")
            raise
    
    def unload_models(self):
        """卸载所有模型（释放内存）"""
        self._base_model = None
        self._voice_design_model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("模型已卸载")
