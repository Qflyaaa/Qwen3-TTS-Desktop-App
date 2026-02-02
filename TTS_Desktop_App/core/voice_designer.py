# coding=utf-8
"""音色设计师"""
import sys
from pathlib import Path
from datetime import datetime

# 添加工作空间路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "Qwen3-TTS"))

from utils.logger import get_logger
from utils.generation_params import GenerationParams

class VoiceDesigner:
    """音色设计师"""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.logger = get_logger()
        self.params_manager = GenerationParams()
    
    def generate_voice_design(self, text, instruct, language="Chinese",
                            output_dir="data/outputs", text_file_name=None,
                            progress_callback=None):
        """
        使用音色设计生成语音
        
        Args:
            text: 文本内容
            instruct: 音色描述
            language: 语言
            output_dir: 输出目录
            text_file_name: 文本文件名（用于命名）
            progress_callback: 进度回调函数
        
        Returns:
            output_path: 生成的音频文件路径
        """
        try:
            if progress_callback:
                progress_callback(20, "正在加载模型...")
            
            model = self.model_loader.get_voice_design_model()
            
            if progress_callback:
                progress_callback(50, "正在生成语音...")
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成输出路径
            safe_name = "".join(c for c in text[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')[:20] if safe_name else "voice_design"
            
            if text_file_name:
                output_filename = f"{text_file_name}_{safe_name}_{timestamp}.wav"
            else:
                output_filename = f"{safe_name}_{timestamp}.wav"
            
            output_path = Path(output_dir) / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成语音
            import soundfile as sf
            wavs, sr = model.generate_voice_design(
                text=text,
                language=language,
                instruct=instruct,
            )
            
            # 保存结果
            sf.write(str(output_path), wavs[0], sr)
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            # 保存生成参数
            params = {
                "generation_type": "voice_design",
                "voice_design": {
                    "text": text,
                    "instruct": instruct,
                    "language": language,
                    "text_file_name": text_file_name
                },
                "model": {
                    "model_type": "VoiceDesign",
                    "model_path": self.model_loader.voice_design_model_path or "Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                    "device": self.model_loader.device,
                    "use_flash_attention": self.model_loader.use_flash_attention
                }
            }
            self.params_manager.save_params(str(output_path), params)
            
            self.logger.info(f"成功生成语音: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"生成语音失败: {e}")
            raise
