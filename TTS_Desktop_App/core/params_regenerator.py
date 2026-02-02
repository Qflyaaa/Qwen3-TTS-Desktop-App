# coding=utf-8
"""根据参数重新生成"""
from pathlib import Path
from utils.logger import get_logger
from utils.generation_params import GenerationParams

class ParamsRegenerator:
    """根据参数重新生成"""
    
    def __init__(self, model_loader, voice_generator, voice_designer):
        self.model_loader = model_loader
        self.voice_generator = voice_generator
        self.voice_designer = voice_designer
        self.params_manager = GenerationParams()
        self.logger = get_logger()
    
    def regenerate_from_params(self, params_file_path: str, 
                              modify_text: str = None,
                              modify_instruct: str = None,
                              progress_callback=None):
        """
        根据参数文件重新生成
        
        Args:
            params_file_path: 参数文件路径
            modify_text: 修改后的文本（可选）
            modify_instruct: 修改后的语气/描述（可选）
            progress_callback: 进度回调
        
        Returns:
            output_path: 新生成的音频文件路径
        """
        try:
            # 加载参数
            params = self.params_manager.load_params(params_file_path)
            
            # 验证参数
            is_valid, msg = self.params_manager.validate_params(params)
            if not is_valid:
                raise ValueError(f"参数验证失败: {msg}")
            
            gen_type = params['generation_type']
            
            if gen_type == 'voice_clone':
                return self._regenerate_voice_clone(params, modify_text, modify_instruct, progress_callback)
            elif gen_type == 'voice_design':
                return self._regenerate_voice_design(params, modify_text, modify_instruct, progress_callback)
            else:
                raise ValueError(f"不支持的生成类型: {gen_type}")
                
        except Exception as e:
            self.logger.error(f"根据参数重新生成失败: {e}")
            raise
    
    def _regenerate_voice_clone(self, params, modify_text, modify_instruct, progress_callback):
        """重新生成语音克隆"""
        vc_params = params['voice_clone']
        
        # 使用修改后的文本或原始文本
        text = modify_text if modify_text else vc_params['text']
        instruct = modify_instruct if modify_instruct is not None else vc_params.get('instruct')
        language = vc_params.get('language', 'Chinese')
        features_path = vc_params['voice_features_path']
        text_file_name = vc_params.get('text_file_name')
        
        # 生成新的音频
        output_path = self.voice_generator.generate_with_voice(
            features_path=features_path,
            text=text,
            instruct=instruct,
            language=language,
            text_file_name=text_file_name,
            progress_callback=progress_callback
        )
        
        return output_path
    
    def _regenerate_voice_design(self, params, modify_text, modify_instruct, progress_callback):
        """重新生成音色设计"""
        vd_params = params['voice_design']
        
        # 使用修改后的文本或原始文本
        text = modify_text if modify_text else vd_params['text']
        instruct = modify_instruct if modify_instruct else vd_params['instruct']
        language = vd_params.get('language', 'Chinese')
        text_file_name = vd_params.get('text_file_name')
        
        # 生成新的音频
        output_path = self.voice_designer.generate_voice_design(
            text=text,
            instruct=instruct,
            language=language,
            text_file_name=text_file_name,
            progress_callback=progress_callback
        )
        
        return output_path
    
    def batch_regenerate(self, params_file_paths: list, 
                        modify_texts: list = None,
                        modify_instructs: list = None,
                        progress_callback=None):
        """
        批量根据参数重新生成
        
        Args:
            params_file_paths: 参数文件路径列表
            modify_texts: 修改后的文本列表（可选，与params_file_paths一一对应）
            modify_instructs: 修改后的语气/描述列表（可选）
            progress_callback: 进度回调 (total, current, message)
        
        Returns:
            output_paths: 生成的音频文件路径列表
        """
        output_paths = []
        total = len(params_file_paths)
        
        if modify_texts is None:
            modify_texts = [None] * total
        if modify_instructs is None:
            modify_instructs = [None] * total
        
        for i, params_file_path in enumerate(params_file_paths):
            if progress_callback:
                progress_callback(total, i + 1, f"正在处理 {i+1}/{total}: {Path(params_file_path).name}")
            
            try:
                output_path = self.regenerate_from_params(
                    params_file_path,
                    modify_text=modify_texts[i] if i < len(modify_texts) else None,
                    modify_instruct=modify_instructs[i] if i < len(modify_instructs) else None,
                    progress_callback=lambda p, m: None  # 内部进度不回调
                )
                output_paths.append(output_path)
            except Exception as e:
                self.logger.error(f"批量生成失败 [{i+1}/{total}]: {e}")
                output_paths.append(None)
        
        return output_paths
