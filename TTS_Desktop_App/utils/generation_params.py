# coding=utf-8
"""生成参数保存和加载工具"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from .logger import get_logger

class GenerationParams:
    """生成参数管理类"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def save_params(self, output_audio_path: str, params: Dict[str, Any]) -> str:
        """
        保存生成参数到JSON文件
        
        Args:
            output_audio_path: 输出音频文件路径
            params: 参数字典
        
        Returns:
            params_file_path: 参数文件路径
        """
        try:
            audio_path = Path(output_audio_path)
            params_file_path = audio_path.with_suffix('.json')
            
            # 添加输出音频路径到参数中
            params['output_audio'] = audio_path.name
            params['output_audio_path'] = str(audio_path)
            params['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            params['app_version'] = "1.0.0"
            
            # 保存为JSON
            with open(params_file_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"参数已保存: {params_file_path}")
            return str(params_file_path)
            
        except Exception as e:
            self.logger.error(f"保存参数失败: {e}")
            raise
    
    def load_params(self, params_file_path: str) -> Dict[str, Any]:
        """
        加载生成参数
        
        Args:
            params_file_path: 参数文件路径
        
        Returns:
            params: 参数字典
        """
        try:
            with open(params_file_path, 'r', encoding='utf-8') as f:
                params = json.load(f)
            return params
        except Exception as e:
            self.logger.error(f"加载参数失败: {e}")
            raise
    
    def get_params_file(self, audio_file_path: str) -> Optional[str]:
        """
        根据音频文件路径获取对应的参数文件路径
        
        Args:
            audio_file_path: 音频文件路径
        
        Returns:
            params_file_path: 参数文件路径，如果不存在返回None
        """
        audio_path = Path(audio_file_path)
        params_file_path = audio_path.with_suffix('.json')
        
        if params_file_path.exists():
            return str(params_file_path)
        return None
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证参数是否完整
        
        Args:
            params: 参数字典
        
        Returns:
            (is_valid, error_message)
        """
        if 'generation_type' not in params:
            return False, "缺少生成类型"
        
        gen_type = params['generation_type']
        
        if gen_type == 'voice_clone':
            required = ['voice_clone']
            if 'voice_clone' not in params:
                return False, "缺少语音克隆参数"
            vc_params = params['voice_clone']
            if 'voice_features_path' not in vc_params or 'text' not in vc_params:
                return False, "缺少必要的语音克隆参数"
        
        elif gen_type == 'voice_design':
            required = ['voice_design']
            if 'voice_design' not in params:
                return False, "缺少音色设计参数"
            vd_params = params['voice_design']
            if 'text' not in vd_params or 'instruct' not in vd_params:
                return False, "缺少必要的音色设计参数"
        
        else:
            return False, f"未知的生成类型: {gen_type}"
        
        return True, "参数验证通过"
