# coding=utf-8
"""文件管理工具"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from .logger import get_logger

class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.voices_dir = self.base_dir / "data" / "voices"
        self.audios_dir = self.base_dir / "data" / "audios"
        self.texts_dir = self.base_dir / "data" / "texts"
        self.outputs_dir = self.base_dir / "data" / "outputs"
        self.logger = get_logger()
        
        # 创建目录
        for dir_path in [self.voices_dir, self.audios_dir, 
                        self.texts_dir, self.outputs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def list_voices(self):
        """列出所有音色"""
        voices = []
        for pt_file in self.voices_dir.glob("*.pt"):
            voice_name = pt_file.stem
            meta_file = self.voices_dir / f"{voice_name}_meta.json"
            
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                except:
                    meta = {"created_at": "未知", "usage_count": 0}
            else:
                meta = {"created_at": "未知", "usage_count": 0}
            
            # 获取文件大小
            file_size = pt_file.stat().st_size / (1024 * 1024)  # MB
            
            voices.append({
                "name": voice_name,
                "path": str(pt_file),
                "meta": meta,
                "file_size": f"{file_size:.2f}MB"
            })
        
        return sorted(voices, key=lambda x: x["meta"].get("last_used", ""), reverse=True)
    
    def save_voice_metadata(self, voice_name, metadata):
        """保存音色元数据"""
        meta_file = self.voices_dir / f"{voice_name}_meta.json"
        
        # 添加时间戳
        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果文件已存在，保留使用次数
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    existing_meta = json.load(f)
                    metadata["usage_count"] = existing_meta.get("usage_count", 0)
            except:
                metadata["usage_count"] = 0
        else:
            metadata["usage_count"] = 0
        
        try:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存元数据失败: {e}")
    
    def update_voice_usage(self, voice_name):
        """更新音色使用次数"""
        meta_file = self.voices_dir / f"{voice_name}_meta.json"
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                meta["usage_count"] = meta.get("usage_count", 0) + 1
                meta["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.logger.error(f"更新使用次数失败: {e}")
    
    def delete_voice(self, voice_name):
        """删除音色"""
        pt_file = self.voices_dir / f"{voice_name}.pt"
        meta_file = self.voices_dir / f"{voice_name}_meta.json"
        
        try:
            if pt_file.exists():
                pt_file.unlink()
            if meta_file.exists():
                meta_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"删除音色失败: {e}")
            return False
    
    def list_outputs(self, limit=50):
        """列出生成的音频文件"""
        from .generation_params import GenerationParams
        params_manager = GenerationParams()
        
        outputs = []
        for wav_file in sorted(self.outputs_dir.rglob("*.wav"), 
                             key=lambda x: x.stat().st_mtime, 
                             reverse=True)[:limit]:
            # 检查是否有参数文件
            params_file = params_manager.get_params_file(str(wav_file))
            
            outputs.append({
                "name": wav_file.name,
                "path": str(wav_file),
                "size": wav_file.stat().st_size / (1024 * 1024),  # MB
                "created": datetime.fromtimestamp(wav_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "has_params": params_file is not None,
                "params_file": params_file
            })
        return outputs
    
    def get_statistics(self):
        """获取统计信息"""
        voices = self.list_voices()
        outputs = self.list_outputs(limit=1000)
        
        total_voices = len(voices)
        total_outputs = len(outputs)
        
        # 计算总大小
        total_size = 0
        for voice in voices:
            pt_file = Path(voice["path"])
            if pt_file.exists():
                total_size += pt_file.stat().st_size
        
        for output in outputs:
            output_file = Path(output["path"])
            if output_file.exists():
                total_size += output_file.stat().st_size
        
        return {
            "total_voices": total_voices,
            "total_outputs": total_outputs,
            "total_size_mb": total_size / (1024 * 1024)
        }
