"""
转换历史记录管理器
用于记录和管理文件转换历史
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ConversionHistory:
    """转换历史记录管理器"""
    
    def __init__(self, history_file: str = "conversion_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict[str, Any]] = []
        self.load_history()
        
    def load_history(self):
        """加载历史记录"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.history = []
            
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            
    def add_conversion(self, files: List[str], output_file: str, success: bool, 
                      error_msg: str = "", char_count: int = 0):
        """添加转换记录"""
        record = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "files": [{"name": Path(f).name, "path": f} for f in files],
            "file_count": len(files),
            "output_file": output_file,
            "success": success,
            "error_msg": error_msg,
            "char_count": char_count,
            "date_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.history.insert(0, record)  # 最新的记录在前面
        
        # 限制历史记录数量（保留最近100条）
        if len(self.history) > 100:
            self.history = self.history[:100]
            
        self.save_history()
        
    def add_record(self, record_data: Dict[str, Any]):
        """添加记录（兼容旧接口）"""
        files = [record_data.get('file_path', '')]
        success = record_data.get('success', False)
        error_msg = record_data.get('error', '')
        char_count = record_data.get('content_length', 0)
        
        self.add_conversion(
            files=files,
            output_file="",
            success=success,
            error_msg=error_msg,
            char_count=char_count
        )
        
    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的转换记录"""
        return self.history[:limit]
        
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的转换记录（兼容旧接口）"""
        return self.get_recent_history(limit)
        
    def get_success_count(self) -> int:
        """获取成功转换次数"""
        return sum(1 for record in self.history if record["success"])
        
    def get_total_files_converted(self) -> int:
        """获取总转换文件数"""
        return sum(record["file_count"] for record in self.history)
        
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.save_history()
        
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.history:
            return {
                "total_conversions": 0,
                "success_conversions": 0,
                "total_files": 0,
                "success_rate": 0,
                "total_chars": 0
            }
            
        total_conversions = len(self.history)
        success_conversions = self.get_success_count()
        total_files = self.get_total_files_converted()
        total_chars = sum(record.get("char_count", 0) for record in self.history)
        
        return {
            "total_conversions": total_conversions,
            "success_conversions": success_conversions,
            "total_files": total_files,
            "success_rate": (success_conversions / total_conversions * 100) if total_conversions > 0 else 0,
            "total_chars": total_chars
        } 
