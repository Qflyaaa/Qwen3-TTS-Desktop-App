# Qwen3-TTS 工作空间

Qwen3-TTS 语音合成项目工作空间，包含桌面应用、模型代码和工具脚本。

## 📁 项目结构

```
TTS_workspace/
├── TTS_Desktop_App/          # 桌面应用程序（主要项目）
├── Qwen3-TTS/                # Qwen3-TTS 模型代码和模型文件
├── scripts/                  # 命令行工具脚本
├── input/                    # 输入文件（音频、文本、指令）
├── output/                   # 输出文件（生成的音频）
├── voice_features/           # 音色特征文件（.pt）
└── video/                    # 视频和参考音频
```

## 🚀 快速开始

### 桌面应用（推荐）

进入 `TTS_Desktop_App/` 目录，查看详细说明：

```bash
cd TTS_Desktop_App
python app.py
```

详细文档：**[TTS_Desktop_App/README.md](TTS_Desktop_App/README.md)**

### 命令行工具

使用 `scripts/` 目录下的脚本进行批量处理：

```bash
# 保存音色特征
python scripts/save_voice_features.py --ref_audio video/prompt.wav --ref_text "参考文本" --output voice_features/name.pt

# 使用音色特征生成语音
python scripts/generate_with_features.py --features voice_features/name.pt --text "要朗读的文本"

# 语音设计
python scripts/voice_design.py --text "文本" --instruct "音色描述"
```

详细文档：**[scripts/README.md](scripts/README.md)**

## 📋 环境要求

- Python 3.10+（推荐 3.12）
- Conda 环境：`qwen3-tts`
- CUDA 11.8+（可选，用于GPU加速）

### 环境配置

```bash
# 创建 Conda 环境
conda create -n qwen3-tts python=3.12
conda activate qwen3-tts

# 安装 PyTorch（CUDA 版本）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 安装依赖
pip install "numpy<2.4"
pip install -r TTS_Desktop_App/requirements.txt
```

## 📦 模型文件

**重要**：本项目不包含模型权重文件（.safetensors），需要手动下载。

### 下载模型

1. **使用 pip（推荐）**：
   ```bash
   pip install qwen-tts
   ```

2. **手动下载**：从 [HuggingFace](https://huggingface.co/Qwen) 下载模型到 `Qwen3-TTS/` 目录

需要的模型：
- `Qwen3-TTS-12Hz-1.7B-Base`（语音克隆）
- `Qwen3-TTS-12Hz-1.7B-VoiceDesign`（音色设计）

## 🎯 主要功能

### 桌面应用（TTS_Desktop_App）
- ✅ 语音克隆并保存音色特征
- ✅ 加载音色特征并朗读文本
- ✅ 定制音色并朗读文本
- ✅ 文件管理和参数保存
- ✅ 图形化界面操作

### 命令行工具（scripts）
- ✅ 批量语音克隆
- ✅ 批量文本生成
- ✅ 格式转换工具

## 📚 文档

- **[TTS_Desktop_App/README.md](TTS_Desktop_App/README.md)** - 桌面应用详细说明
- **[TTS_Desktop_App/项目说明.md](TTS_Desktop_App/项目说明.md)** - 项目详细说明（中文）
- **[scripts/README.md](scripts/README.md)** - 命令行工具说明
- **[Qwen3-TTS/README.md](Qwen3-TTS/README.md)** - Qwen3-TTS 模型说明

## ⚙️ 环境激活

Windows 用户可以使用提供的批处理文件：

```bash
# 激活环境并打开终端
activate_env.bat
```

## 🔗 相关链接

- [GitHub 仓库](https://github.com/Qflyaaa/Qwen3-TTS-Desktop-App)
- [Qwen3-TTS 官方仓库](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS HuggingFace](https://huggingface.co/Qwen)

## 📄 许可证

本项目基于 Qwen3-TTS 模型开发。请遵守 Qwen3-TTS 的许可证要求。

---

**注意**：本项目仅包含应用代码，不包含模型文件。使用前请确保已下载相应的模型文件。
