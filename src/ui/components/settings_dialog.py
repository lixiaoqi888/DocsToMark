"""
设置对话框组件
包含应用配置和主题设置
"""

import flet as ft
from typing import Callable, Optional, Dict, Any


class SettingsDialog(ft.AlertDialog):
    """设置对话框"""
    
    def __init__(
        self,
        page: ft.Page,
        on_settings_changed: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        self.page = page
        self.on_settings_changed = on_settings_changed
        
        # 获取当前主题
        current_theme = "system"
        if page.theme_mode == ft.ThemeMode.LIGHT:
            current_theme = "light"
        elif page.theme_mode == ft.ThemeMode.DARK:
            current_theme = "dark"
            
        # 创建主题选择器
        self.theme_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="system", label="跟随系统"),
                ft.Radio(value="light", label="浅色主题"),
                ft.Radio(value="dark", label="深色主题")
            ], tight=True, spacing=5),
            value=current_theme
        )
        
        # 创建文件大小限制设置
        self.file_size_limit = ft.TextField(
            label="文件大小限制 (MB)",
            value="100",
            width=150,
            input_filter=ft.NumbersOnlyInputFilter(),
            dense=True
        )
        
        # 创建默认保存格式设置
        self.default_format = ft.Dropdown(
            label="默认保存格式",
            value="markdown",
            options=[
                ft.dropdown.Option("markdown", "Markdown (.md)"),
                ft.dropdown.Option("text", "纯文本 (.txt)")
            ],
            width=200,
            dense=True
        )
        
        # 创建对话框内容
        super().__init__(
            title=ft.Text("应用设置", size=20, weight=ft.FontWeight.BOLD),
            content=self.create_content(),
            actions=[
                ft.TextButton("取消", on_click=self.close_dialog),
                ft.ElevatedButton("保存", on_click=self.save_settings)
            ],
            modal=True,
            actions_alignment=ft.MainAxisAlignment.END,
            **kwargs
        )
    
    def create_content(self) -> ft.Container:
        """创建对话框内容"""
        # 创建一个明确大小的容器 - 这是关键
        content_container = ft.Container(
            content=ft.Column([
                # 主题设置区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎨 主题设置", size=16, weight=ft.FontWeight.BOLD),
                        self.theme_radio,
                    ], spacing=8, tight=True),
                    padding=ft.padding.all(10),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    bgcolor=ft.Colors.BLUE_50
                ),
                
                # 转换设置区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("⚙️ 转换设置", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.file_size_limit,
                            self.default_format
                        ], spacing=10),
                    ], spacing=8, tight=True),
                    padding=ft.padding.all(10),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                    bgcolor=ft.Colors.GREEN_50
                ),
                
                # 关于信息区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("ℹ️ 关于", size=16, weight=ft.FontWeight.BOLD),
                        ft.Column([
                            ft.Text("MarkItDown 智能转换器", weight=ft.FontWeight.BOLD),
                            ft.Text("版本: v2.0.0", size=12),
                            ft.Text("公众号：AI康康老师", size=12, color=ft.Colors.BLUE_600),
                            ft.Text("基于 Microsoft MarkItDown", size=12),
                            ft.Text("完全离线运行，保护数据隐私", size=12, color=ft.Colors.GREEN)
                        ], spacing=3, tight=True)
                    ], spacing=8, tight=True),
                    padding=ft.padding.all(10),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    bgcolor=ft.Colors.GREY_50
                )
            ], 
            spacing=12,
            tight=True,
            scroll=ft.ScrollMode.AUTO
            ),
            # 明确设置容器尺寸 - 这是确保内容显示的关键
            width=550,
            height=450,
            padding=ft.padding.all(20)
        )
        
        return content_container
        
    def close_dialog(self, e):
        """关闭对话框"""
        self.open = False
        if self.page:
            self.page.update()
            
    def save_settings(self, e):
        """保存设置"""
        try:
            # 应用主题设置
            theme_value = self.theme_radio.value
            if self.page:
                if theme_value == "light":
                    self.page.theme_mode = ft.ThemeMode.LIGHT
                elif theme_value == "dark":
                    self.page.theme_mode = ft.ThemeMode.DARK
                else:
                    self.page.theme_mode = ft.ThemeMode.SYSTEM
            
            # 收集设置数据
            settings_data = {
                "theme": theme_value,
                "file_size_limit_mb": int(self.file_size_limit.value or "100"),
                "default_format": self.default_format.value
            }
            
            # 保存设置到本地文件
            self.save_settings_to_file(settings_data)
            
            # 通知父组件设置已更改
            if self.on_settings_changed:
                self.on_settings_changed(settings_data)
            
            if self.page:
                self.page.update()
            self.close_dialog(e)
            
        except Exception as ex:
            # 显示错误信息 - 简化处理避免dialog兼容性问题
            print(f"设置保存失败: {str(ex)}")
            self.close_dialog(e)
            
    def save_settings_to_file(self, settings: Dict[str, Any]):
        """保存设置到文件"""
        import json
        import tempfile
        from pathlib import Path
        
        try:
            settings_file = Path(tempfile.gettempdir()) / "markitdown_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception:
            # 如果保存失败，不影响应用运行
            pass
            
    @staticmethod
    def load_settings() -> Dict[str, Any]:
        """从文件加载设置"""
        import json
        import tempfile
        from pathlib import Path
        
        default_settings = {
            "theme": "system",
            "file_size_limit_mb": 100,
            "default_format": "markdown"
        }
        
        try:
            settings_file = Path(tempfile.gettempdir()) / "markitdown_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # 合并默认设置和保存的设置
                    default_settings.update(saved_settings)
        except Exception:
            # 如果加载失败，使用默认设置
            pass
            
        return default_settings 
