"""
批量UI更新管理器
减少page.update()调用频率，提升性能
"""

import flet as ft
import time
from typing import List, Callable
import threading


class BatchUpdater:
    """批量UI更新管理器"""
    
    def __init__(self, page: ft.Page, batch_delay: float = 0.1):
        self.page = page
        self.batch_delay = batch_delay  # 批量延迟时间（秒）
        self._pending_updates: List[Callable] = []
        self._update_timer = None
        self._lock = threading.Lock()
    
    def schedule_update(self, update_func: Callable = lambda: None):
        """安排一个UI更新"""
        with self._lock:
            if update_func and update_func != (lambda: None):
                self._pending_updates.append(update_func)
            
            # 取消之前的计时器
            if self._update_timer:
                self._update_timer.cancel()
            
            # 设置新的计时器
            self._update_timer = threading.Timer(self.batch_delay, self._execute_batch_update)
            self._update_timer.start()
    
    def _execute_batch_update(self):
        """执行批量更新"""
        with self._lock:
            if self._pending_updates:
                try:
                    # 执行所有待处理的更新函数
                    for update_func in self._pending_updates:
                        try:
                            update_func()
                        except Exception as e:
                            print(f"更新函数执行失败: {e}")
                    
                    # 执行一次UI更新
                    if self.page:
                        self.page.update()
                    
                    # 清空待处理列表
                    self._pending_updates.clear()
                    
                except Exception as e:
                    print(f"批量更新失败: {e}")
            
            self._update_timer = None
    
    def immediate_update(self):
        """立即执行更新（紧急情况使用）"""
        with self._lock:
            if self._update_timer:
                self._update_timer.cancel()
                self._update_timer = None
            self._execute_batch_update()


class UICache:
    """UI组件缓存管理器"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
        self._access_order = []
    
    def get(self, key: str):
        """获取缓存的组件"""
        if key in self._cache:
            # 更新访问顺序
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def put(self, key: str, component):
        """缓存组件"""
        if key in self._cache:
            # 更新现有缓存
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # 移除最久未使用的缓存
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = component
        self._access_order.append(key)
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class PerformanceManager:
    """性能管理器 - 集成批量更新和缓存"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.batch_updater = BatchUpdater(page)
        self.ui_cache = UICache()
        self._operation_counts = {}
    
    def schedule_ui_update(self, update_func: Callable = lambda: None):
        """安排UI更新"""
        self.batch_updater.schedule_update(update_func)
    
    def immediate_ui_update(self):
        """立即更新UI"""
        self.batch_updater.immediate_update()
    
    def cache_component(self, key: str, component):
        """缓存UI组件"""
        self.ui_cache.put(key, component)
    
    def get_cached_component(self, key: str):
        """获取缓存的UI组件"""
        return self.ui_cache.get(key)
    
    def track_operation(self, operation_name: str):
        """跟踪操作次数"""
        if operation_name not in self._operation_counts:
            self._operation_counts[operation_name] = 0
        self._operation_counts[operation_name] += 1
    
    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        return {
            "cache_size": self.ui_cache.size(),
            "operation_counts": self._operation_counts.copy(),
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        total_gets = self._operation_counts.get("cache_get", 0)
        hits = self._operation_counts.get("cache_hit", 0)
        return (hits / total_gets * 100) if total_gets > 0 else 0.0 