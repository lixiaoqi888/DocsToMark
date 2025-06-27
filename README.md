# DocsToMark

A beautiful desktop application for converting various document formats to Markdown, powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

## ✨ Features

- 🖱️ **Easy to Use**: Intuitive GUI interface with drag & drop support
- 📁 **Multiple Formats**: PDF, Word, Excel, PowerPoint, images, audio files, and more
- 👀 **Live Preview**: Real-time preview of conversion results
- 💾 **Batch Processing**: Convert multiple files at once
- 🚀 **Offline**: Completely local processing, no internet required
- 🔒 **Private**: All files are processed locally, nothing uploaded
- 🎨 **Modern UI**: Beautiful, responsive interface built with Flet

## 📋 Supported Formats

- **Documents**: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls)
- **Images**: JPG, PNG, GIF, BMP (with OCR support)
- **Audio**: WAV, MP3 (speech-to-text)
- **Web**: HTML, XML
- **Data**: CSV, JSON
- **Archives**: ZIP files
- **E-books**: EPUB
- **Others**: Plain text files

## 🚀 Quick Start

### Requirements
- Python 3.10+
- Windows, macOS, or Linux

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DocsToMark.git
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

## 💡 Usage

1. **Add Files**: Click "Browse Files" or drag & drop files into the application
2. **Convert**: Click "Convert to Markdown" to process your files
3. **Preview**: View results in the built-in editor
4. **Save**: Export your converted Markdown files

## 🛠️ Tech Stack

- **Framework**: [Flet](https://flet.dev/) (Python GUI)
- **Conversion Engine**: [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- **Language**: Python 3.10+

## 📦 Building Executable

To create a standalone executable:

```bash
flet pack main.py --name "DocsToMark" --add-data "src:src"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) for the powerful conversion engine
- [Flet](https://flet.dev/) for the amazing Python GUI framework 