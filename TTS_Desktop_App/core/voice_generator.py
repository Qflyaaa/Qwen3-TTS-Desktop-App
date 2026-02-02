# coding=utf-8
"""语音生成器"""
import sys
from pathlib import Path
from datetime import datetime

# 添加工作空间路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "Qwen3-TTS"))
sys.path.insert(0, str(WORKSPACE_ROOT / "scripts"))

from utils.logger import get_logger
from utils.file_manager import FileManager
from utils.generation_params import GenerationParams

class VoiceGenerator:
    """语音生成器"""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.logger = get_logger()
        self.file_manager = FileManager()
        self.params_manager = GenerationParams()
    
    def generate_with_voice(self, features_path, text, instruct=None,
                           language="Chinese", output_dir="data/outputs",
                           text_file_name=None, progress_callback=None):
        """
        使用保存的音色特征生成语音
        
        Args:
            features_path: 特征文件路径
            text: 文本内容
            instruct: 语气指令（可选）
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
            
            model = self.model_loader.get_base_model()
            
            if progress_callback:
                progress_callback(40, "正在加载音色特征...")
            
            # 加载特征
            prompt_items = self._load_voice_features(features_path)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成输出路径
            voice_name = Path(features_path).stem
            if text_file_name:
                output_filename = f"{voice_name}_{text_file_name}_{timestamp}.wav"
            else:
                output_filename = f"{voice_name}_{timestamp}.wav"
            
            output_path = Path(output_dir) / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if instruct:
                # 使用带语气控制的生成
                if progress_callback:
                    progress_callback(60, "正在生成语音（带语气控制）...")
                output_path = self._generate_with_emotion(
                    model, prompt_items, text, instruct, language, str(output_path)
                )
            else:
                # 使用普通生成
                if progress_callback:
                    progress_callback(60, "正在生成语音...")
                output_path = self._generate_normal(
                    model, prompt_items, text, language, str(output_path)
                )
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            # 更新使用次数
            self.file_manager.update_voice_usage(voice_name)
            
            # 保存生成参数
            params = {
                "generation_type": "voice_clone",
                "voice_clone": {
                    "voice_features_path": str(features_path),
                    "voice_name": voice_name,
                    "text": text,
                    "instruct": instruct,
                    "language": language,
                    "text_file_name": text_file_name
                },
                "model": {
                    "model_type": "Base",
                    "model_path": self.model_loader.base_model_path or "Qwen3-TTS-12Hz-1.7B-Base",
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
    
    def _load_voice_features(self, features_path):
        """加载语音特征"""
        import torch
        from qwen_tts import VoiceClonePromptItem
        
        device = self.model_loader.device
        
        payload = torch.load(features_path, map_location=device)
        items_data = payload.get("items", [])
        
        prompt_items = []
        for item_dict in items_data:
            item = VoiceClonePromptItem(
                ref_code=item_dict["ref_code"].to(device) if item_dict["ref_code"] is not None else None,
                ref_spk_embedding=item_dict["ref_spk_embedding"].to(device),
                x_vector_only_mode=item_dict["x_vector_only_mode"],
                icl_mode=item_dict["icl_mode"],
                ref_text=item_dict["ref_text"],
            )
            prompt_items.append(item)
        
        return prompt_items
    
    def _generate_normal(self, model, prompt_items, text, language, output_path):
        """普通生成（无语气控制）"""
        import soundfile as sf
        
        wavs, sr = model.generate_voice_clone(
            text=text,
            language=language,
            voice_clone_prompt=prompt_items,
        )
        
        sf.write(output_path, wavs[0], sr)
        return output_path
    
    def _generate_with_emotion(self, model, prompt_items, text, instruct, language, output_path):
        """带语气控制的生成"""
        import soundfile as sf
        import torch
        
        # 转换 prompt items 为 voice_clone_prompt 字典
        voice_clone_prompt_dict = model._prompt_items_to_voice_clone_prompt(prompt_items)
        
        # 准备文本和语言
        texts = [text]
        languages = [language]
        
        # 构建输入文本
        input_texts = [model._build_assistant_text(t) for t in texts]
        input_ids = model._tokenize_texts(input_texts)
        
        # 构建语气指令
        instruct_texts = [model._build_instruct_text(instruct)]
        instruct_ids = model._tokenize_texts(instruct_texts)
        
        # 准备 ref_ids
        ref_ids = None
        ref_texts_for_ids = [item.ref_text for item in prompt_items]
        if ref_texts_for_ids and ref_texts_for_ids[0]:
            ref_ids = []
            for rt in ref_texts_for_ids:
                if rt is None or rt == "":
                    ref_ids.append(None)
                else:
                    ref_tok = model._tokenize_texts([model._build_ref_text(rt)])[0]
                    ref_ids.append(ref_tok)
        
        # 合并生成参数
        gen_kwargs = model._merge_generate_kwargs()
        
        # 调用底层模型的 generate 方法
        talker_codes_list, _ = model.model.generate(
            input_ids=input_ids,
            ref_ids=ref_ids,
            voice_clone_prompt=voice_clone_prompt_dict,
            instruct_ids=instruct_ids,
            languages=languages,
            non_streaming_mode=False,
            **gen_kwargs,
        )
        
        # 解码音频
        codes_for_decode = []
        for i, codes in enumerate(talker_codes_list):
            ref_code_list = voice_clone_prompt_dict.get("ref_code", None)
            if ref_code_list is not None and ref_code_list[i] is not None:
                codes_for_decode.append(torch.cat([ref_code_list[i].to(codes.device), codes], dim=0))
            else:
                codes_for_decode.append(codes)
        
        wavs_all, fs = model.model.speech_tokenizer.decode([{"audio_codes": c} for c in codes_for_decode])
        
        # 处理输出音频（移除参考音频部分）
        wavs_out = []
        for i, wav in enumerate(wavs_all):
            ref_code_list = voice_clone_prompt_dict.get("ref_code", None)
            if ref_code_list is not None and ref_code_list[i] is not None:
                ref_len = int(ref_code_list[i].shape[0])
                total_len = int(codes_for_decode[i].shape[0])
                cut = int(ref_len / max(total_len, 1) * wav.shape[0])
                wavs_out.append(wav[cut:])
            else:
                wavs_out.append(wav)
        
        # 保存结果
        sf.write(output_path, wavs_out[0], fs)
        return output_path
