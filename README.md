# DocsToMark

A beautiful desktop application for converting various document formats to Markdown, powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

[中文文档](#中文文档) | [English](#english)

## English

### ✨ Features

- 🖱️ **Easy to Use**: Intuitive GUI interface with drag & drop support
- 📁 **Multiple Formats**: PDF, Word, Excel, PowerPoint, images, audio files, and more
- 👀 **Live Preview**: Real-time preview of conversion results
- 💾 **Batch Processing**: Convert multiple files at once
- 🚀 **Offline**: Completely local processing, no internet required
- 🔒 **Private**: All files are processed locally, nothing uploaded
- 🎨 **Modern UI**: Beautiful, responsive interface built with Flet

### 📋 Supported Formats

- **Documents**: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls)
- **Images**: JPG, PNG, GIF, BMP (with OCR support)
- **Audio**: WAV, MP3 (speech-to-text)
- **Web**: HTML, XML
- **Data**: CSV, JSON
- **Archives**: ZIP files
- **E-books**: EPUB
- **Others**: Plain text files

### 🚀 Quick Start

#### Requirements
- Python 3.10+
- Windows, macOS, or Linux

#### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lixiaoqi888/DocsToMark.git
   cd DocsToMark
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### 💡 Usage

1. **Add Files**: Click "Browse Files" or drag & drop files into the application
2. **Convert**: Click "Convert to Markdown" to process your files
3. **Preview**: View results in the built-in editor
4. **Save**: Export your converted Markdown files

### 🛠️ Tech Stack

- **Framework**: [Flet](https://flet.dev/) (Python GUI)
- **Conversion Engine**: [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- **Language**: Python 3.10+

### 📦 Building Executable

To create a standalone executable:

```bash
flet pack main.py --name "DocsToMark" --add-data "src:src"
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) for the powerful conversion engine
- [Flet](https://flet.dev/) for the amazing Python GUI framework

---

## 中文文档

基于 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 的可视化桌面应用程序，让用户轻松将各种文件格式转换为 Markdown。

### ✨ 功能特点

- 🖱️ **简单易用**：直观的图形界面，支持拖拽操作
- 📁 **支持多种格式**：PDF、Word、Excel、PowerPoint、图片、音频等
- 👀 **实时预览**：转换结果即时预览
- 💾 **批量处理**：支持同时转换多个文件
- 🚀 **离线使用**：完全本地处理，无需网络连接
- 🔒 **隐私安全**：所有文件在本地处理，不上传任何数据
- 🎨 **现代界面**：基于 Flet 的精美响应式界面

### 📋 支持的文件格式

- **文档类**: PDF、Word (.docx)、PowerPoint (.pptx)、Excel (.xlsx, .xls)
- **图片类**: JPG、PNG、GIF、BMP（支持 OCR 文字识别）
- **音频类**: WAV、MP3（支持语音转文字）
- **网页类**: HTML、XML
- **数据类**: CSV、JSON
- **压缩包**: ZIP 文件
- **电子书**: EPUB
- **其他**: 纯文本文件等

### 🚀 快速开始

#### 环境要求
- Python 3.10+
- Windows、macOS 或 Linux

#### 安装方法

1. 克隆仓库：
   ```bash
   git clone https://github.com/lixiaoqi888/DocsToMark.git
   cd DocsToMark
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```bash
   python main.py
   ```

### 💡 使用方法

1. **添加文件**：点击"浏览文件"按钮或拖拽文件到应用中
2. **开始转换**：点击"转换为 Markdown"按钮处理文件
3. **预览结果**：在内置编辑器中查看转换结果
4. **保存文件**：导出转换后的 Markdown 文件

### 🛠️ 技术栈

- **界面框架**：[Flet](https://flet.dev/)（Python GUI）
- **转换引擎**：[Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- **开发语言**：Python 3.10+

### 📦 打包为可执行文件

创建独立的可执行文件：

```bash
flet pack main.py --name "DocsToMark" --add-data "src:src"
```

### 🤝 贡献

欢迎贡献代码！请随时提交 Pull Request。

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- 感谢 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 提供强大的转换引擎
- 感谢 [Flet](https://flet.dev/) 提供优秀的 Python GUI 框架
