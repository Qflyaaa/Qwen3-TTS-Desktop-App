# coding=utf-8
"""语音克隆管理器"""
import sys
from pathlib import Path
from datetime import datetime

# 添加工作空间路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "Qwen3-TTS"))
sys.path.insert(0, str(WORKSPACE_ROOT / "scripts"))

from qwen_tts import Qwen3TTSModel, VoiceClonePromptItem
from utils.logger import get_logger
from utils.file_manager import FileManager

class VoiceCloneManager:
    """语音克隆管理器"""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.logger = get_logger()
        self.file_manager = FileManager()
    
    def extract_features(self, ref_audio_path, ref_text, voice_name, 
                        x_vector_only=False, progress_callback=None):
        """
        提取并保存语音特征
        
        Args:
            ref_audio_path: 参考音频路径
            ref_text: 参考文本
            voice_name: 音色名称
            x_vector_only: 是否仅使用X-Vector
            progress_callback: 进度回调函数 (progress, message)
        
        Returns:
            output_path: 保存的特征文件路径
        """
        try:
            # 加载模型
            if progress_callback:
                progress_callback(10, "正在加载模型...")
            model = self.model_loader.get_base_model()
            
            # 提取特征
            if progress_callback:
                progress_callback(30, "正在提取语音特征...")
            prompt_items = model.create_voice_clone_prompt(
                ref_audio=ref_audio_path,
                ref_text=ref_text,
                x_vector_only_mode=x_vector_only,
            )
            
            # 保存特征
            if progress_callback:
                progress_callback(70, "正在保存特征文件...")
            output_path = self._save_features(
                prompt_items, voice_name, ref_audio_path, ref_text, x_vector_only, model
            )
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            self.logger.info(f"成功提取并保存音色特征: {voice_name}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"提取特征失败: {e}")
            raise
    
    def _save_features(self, prompt_items, voice_name, ref_audio_path, 
                      ref_text, x_vector_only, model):
        """保存特征文件"""
        import torch
        
        # 确保输出目录存在
        output_dir = Path(__file__).parent.parent / "data" / "voices"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{voice_name}.pt"
        
        # 转换为可序列化的格式
        items_data = []
        for item in prompt_items:
            item_dict = {
                "ref_code": item.ref_code.cpu() if item.ref_code is not None else None,
                "ref_spk_embedding": item.ref_spk_embedding.cpu(),
                "x_vector_only_mode": item.x_vector_only_mode,
                "icl_mode": item.icl_mode,
                "ref_text": item.ref_text,
            }
            items_data.append(item_dict)
        
        # 保存元数据
        metadata = {
            "ref_audio_path": str(ref_audio_path),
            "ref_text": ref_text,
            "x_vector_only_mode": x_vector_only,
            "num_items": len(items_data),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 保存为 .pt 文件
        payload = {
            "metadata": metadata,
            "items": items_data,
        }
        
        torch.save(payload, output_path)
        
        # 保存元数据到JSON
        self.file_manager.save_voice_metadata(voice_name, metadata)
        
        return str(output_path)
