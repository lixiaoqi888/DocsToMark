"""
最近文件管理器
管理最近转换的文件列表，提供快速访问
"""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class RecentFilesManager:
    """最近文件管理器"""
    
    def __init__(self, max_recent: int = 10):
        self.max_recent = max_recent
        self.recent_file = Path(tempfile.gettempdir()) / "markitdown_recent_files.json"
        self.recent_files: List[Dict[str, Any]] = []
        self.load_recent_files()
        
    def load_recent_files(self):
        """从文件加载最近文件列表"""
        try:
            if self.recent_file.exists():
                with open(self.recent_file, 'r', encoding='utf-8') as f:
                    self.recent_files = json.load(f)
        except Exception:
            self.recent_files = []
            
    def save_recent_files(self):
        """保存最近文件列表到文件"""
        try:
            with open(self.recent_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 保存失败不影响程序运行
            
    def add_recent_file(self, file_path: str, success: bool = True):
        """添加文件到最近列表"""
        if not os.path.exists(file_path):
            return
            
        file_info = {
            "path": file_path,
            "name": Path(file_path).name,
            "size": os.path.getsize(file_path),
            "modified": os.path.getmtime(file_path),
            "added": datetime.now().isoformat(),
            "success": success
        }
        
        # 移除已存在的同名文件
        self.recent_files = [f for f in self.recent_files if f["path"] != file_path]
        
        # 添加到开头
        self.recent_files.insert(0, file_info)
        
        # 限制列表长度
        if len(self.recent_files) > self.max_recent:
            self.recent_files = self.recent_files[:self.max_recent]
            
        self.save_recent_files()
        
    def get_recent_files(self) -> List[Dict[str, Any]]:
        """获取最近文件列表"""
        # 过滤掉不存在的文件
        valid_files = []
        for file_info in self.recent_files:
            if os.path.exists(file_info["path"]):
                valid_files.append(file_info)
        
        # 如果列表有变化，保存更新
        if len(valid_files) != len(self.recent_files):
            self.recent_files = valid_files
            self.save_recent_files()
            
        return self.recent_files
        
    def clear_recent_files(self):
        """清空最近文件列表"""
        self.recent_files = []
        self.save_recent_files()
        
    def remove_recent_file(self, file_path: str):
        """从最近列表中移除指定文件"""
        self.recent_files = [f for f in self.recent_files if f["path"] != file_path]
        self.save_recent_files()
        
    def get_file_size_string(self, size_bytes: int) -> str:
        """获取文件大小的友好显示"""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB" 