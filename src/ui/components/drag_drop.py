"""
文件选择组件 - 改进版
基于点击选择的用户友好文件选择器
"""

import flet as ft
from typing import List, Callable, Optional


class FileSelectArea(ft.Container):
    """文件选择区域组件
    
    提供用户友好的文件选择体验
    """
    
    def __init__(
        self,
        on_files_selected: Optional[Callable[[List[str]], None]] = None,
        on_click_callback: Optional[Callable[[], None]] = None,
        width: int = 300,
        height: int = 200,
        **kwargs
    ):
        self.on_files_selected = on_files_selected
        self.on_click_callback = on_click_callback
        self._file_count = 0
        
        # 创建内容
        content = ft.Column([
            ft.Icon("upload_file", size=48, color=ft.Colors.BLUE_400),
            ft.Text(
                "点击选择文件",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_600
            ),
            ft.Text(
                "支持多种格式转换",
                size=12,
                color=ft.Colors.BLUE_400
            ),
            ft.Text(
                "PDF • Word • Excel • 图片 • 音频",
                size=10,
                color=ft.Colors.GREY_500,
                italic=True
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        super().__init__(
            content=content,
            width=width,
            height=height,
            border=ft.border.all(2, ft.Colors.BLUE_300),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50,
            alignment=ft.alignment.center,
            on_click=self.handle_click,
            **kwargs
        )
        
    def handle_click(self, e):
        """处理点击事件 - 触发文件选择"""
        if self.on_click_callback:
            self.on_click_callback()
        
    def update_file_count(self, count: int):
        """更新文件计数显示"""
        self._file_count = count
        if count > 0:
            self.content.controls[1].value = f"已选择 {count} 个文件"
            self.content.controls[2].value = "点击添加更多文件"
        else:
            self.content.controls[1].value = "点击选择文件"
            self.content.controls[2].value = "支持多种格式转换"
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
        
    def update_status(self, message: str, is_error: bool = False):
        """更新显示状态"""
        if len(self.content.controls) >= 3:
            self.content.controls[2].value = message
            if is_error:
                self.content.controls[2].color = ft.Colors.RED_500
            else:
                self.content.controls[2].color = ft.Colors.BLUE_400
            
            if hasattr(self, 'page') and self.page:
                self.page.update()


def create_file_selector_with_preview(
    on_files_selected: Callable[[List[str]], None],
    file_picker: ft.FilePicker
) -> ft.Container:
    """创建带预览的文件选择器
    
    这是推荐的文件选择方案
    """
    
    def open_file_picker():
        file_picker.pick_files(
            dialog_title="选择要转换的文件",
            allow_multiple=True,
            file_type=ft.FilePickerFileType.ANY
        )
    
    selector = FileSelectArea(
        on_click_callback=open_file_picker,
        width=400,
        height=150
    )
    
    return ft.Container(
        content=ft.Column([
            ft.Text("📁 文件选择", weight=ft.FontWeight.BOLD),
            selector,
            ft.Text(
                "💡 提示：点击上方区域选择文件，支持多文件选择",
                size=12,
                color=ft.Colors.GREY_600
            )
        ], spacing=10),
        padding=10
    ) 
