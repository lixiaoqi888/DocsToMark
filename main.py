#!/usr/bin/env python3
"""
MarkItDown 可视化转换器 - 美化版界面
现代化设计，用户友好的交互体验
"""

import flet as ft
import os
import json
from pathlib import Path
from datetime import datetime
import logging
from markitdown import MarkItDown

# 导入历史记录和最近文件管理器
from src.history_manager import ConversionHistory
from src.recent_files import RecentFilesManager

# 导入性能管理器
try:
    from src.ui.components.batch_updater import PerformanceManager
except ImportError:
    PerformanceManager = None

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('markitdown_beautiful.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeautifulMarkItDownApp:
    """MarkItDown 美化版应用"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page_theme()
        
        # 配置文件
        self.config_file = "app_config.json"
        self.config = self.load_config()
        
        # 转换器
        self.converter = None
        
        # 初始化历史记录和最近文件管理器
        self.history_manager = ConversionHistory()
        self.recent_files_manager = RecentFilesManager()
        
        # 初始化性能管理器（延迟到page设置后）
        self.performance_manager = None
        
        # UI组件
        self.selected_files = []
        self.conversion_results = {}  # 存储每个文件的转换结果
        self.current_selected_file = None  # 当前选中的文件
        
        # 页面状态管理
        self.current_page = "main"  # main, settings
        self.settings_page = None
        
        # 响应式布局状态
        self.is_mobile_layout = False
        
        self.init_components()
        self.init_ui()
        self.init_converter()
    
    def setup_page_theme(self):
        """设置页面主题"""
        self.page.title = "✨ MarkItDown 智能转换器"
        
        # 从保存的设置中加载主题
        from src.ui.settings_page import SettingsPage
        saved_settings = SettingsPage.load_settings()
        saved_theme = saved_settings.get("theme", "light")
        
        # 应用保存的主题
        if saved_theme == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            
        self.page.window.width = 1200
        self.page.window.height = 900
        self.page.window.min_width = 800  # 降低最小宽度以支持更小屏幕
        self.page.window.min_height = 600  # 降低最小高度
        
        # 自定义主题色彩
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            visual_density=ft.VisualDensity.COMFORTABLE
        )
        
        # 设置页面背景
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.padding = 0
        
        # 监听窗口大小变化
        self.page.on_resized = self.on_window_resized
    
    def load_config(self):
        """加载配置"""
        default_config = {
            "openai_api_key": "",
            "azure_endpoint": "",
            "enable_basic": True,
            "enable_azure": False,
            "enable_llm": False,
            "theme_mode": "light",
            "file_size_limits": {
                "pdf": 50, "pptx": 100, "docx": 50, "xlsx": 25,
                "jpg": 10, "png": 10, "mp3": 100, "wav": 100
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except json.JSONDecodeError as e:
                logger.error(f"配置文件JSON格式错误: {e}")
            except FileNotFoundError:
                logger.info("配置文件不存在，将使用默认配置")
            except PermissionError as e:
                logger.error(f"无权限读取配置文件: {e}")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except PermissionError as e:
            logger.error(f"无权限写入配置文件: {e}")
        except OSError as e:
            logger.error(f"磁盘空间不足或路径无效: {e}")
        except TypeError as e:
            logger.error(f"配置数据类型错误: {e}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def init_components(self):
        """初始化UI组件"""
        # 文件列表
        self.file_list_view = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=300
        )
        
        # 空状态显示
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.FOLDER_OPEN_OUTLINED,
                    size=32,
                    color=ft.Colors.GREY_300
                ),
                ft.Text(
                    "还没有选择文件",
                    size=13,
                    color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "点击上方按钮开始添加",
                    size=11,
                    color=ft.Colors.GREY_300,
                    text_align=ft.TextAlign.CENTER
                )
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
            ),
            expand=True,
            alignment=ft.alignment.center
        )
        
        # 结果显示
        self.result_text = ft.TextField(
            multiline=True,
            expand=True,
            read_only=True,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_color=ft.Colors.TRANSPARENT,
            hint_text="转换结果将在这里显示...",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_400)
        )
        
        # 状态显示
        self.status_text = ft.Text(
            "🚀 准备就绪，选择文件开始转换",
            size=14,
            color=ft.Colors.GREY_600,
            weight=ft.FontWeight.BOLD
        )
        
        # 进度条
        self.progress_bar = ft.ProgressBar(
            visible=False,
            height=4,
            bgcolor=ft.Colors.GREY_200,
            color=ft.Colors.BLUE
        )
        
        # 拖拽区域
        self.drag_area = self.create_drag_area()
    
    def get_file_list_content(self):
        """获取文件列表内容 - 如果没有文件显示空状态"""
        if len(self.selected_files) == 0:
            return self.empty_state
        else:
            return self.file_list_view
    
    def refresh_file_list_display(self):
        """刷新文件列表显示"""
        # 找到文件列表容器并更新其内容
        if hasattr(self, 'file_list_container'):
            # 只有当内容确实改变时才更新
            new_content = self.get_file_list_content()
            if self.file_list_container.content != new_content:
                self.file_list_container.content = new_content
                # 使用性能管理器批量更新UI
                if self.performance_manager:
                    self.performance_manager.schedule_ui_update()
        else:
            self.page.update()
        # 移除不必要的else分支
    
    def create_drag_area(self):
        """创建拖拽上传区域"""
        # 根据布局模式调整拖拽区域的尺寸
        is_mobile = hasattr(self, 'is_mobile_layout') and self.is_mobile_layout
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.CLOUD_UPLOAD_OUTLINED,
                    size=40 if is_mobile else 48,  # 小屏幕时减小图标
                    color=ft.Colors.BLUE_300
                ),
                ft.Text(
                    "拖拽文件到这里",
                    size=16 if is_mobile else 18,  # 小屏幕时减小文字
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700
                ),
                ft.Text(
                    "或点击选择文件",
                    size=13 if is_mobile else 14,  # 小屏幕时减小文字
                    color=ft.Colors.GREY_600
                ),
                ft.Container(height=8 if is_mobile else 10),
                ft.Row([
                    self.create_format_chip("PDF"),
                    self.create_format_chip("DOCX"),
                    self.create_format_chip("XLSX"),
                    self.create_format_chip("PPTX"),
                    self.create_format_chip("TXT"),
                    self.create_format_chip("HTML"),
                    self.create_format_chip("图片"),
                    self.create_format_chip("音频"),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            # 响应式高度
            height=160 if is_mobile else 200,
            border_radius=16,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            bgcolor=ft.Colors.BLUE_50,
            padding=16 if is_mobile else 20,  # 小屏幕时减少padding
            on_click=self.pick_files,
            ink=True,
            expand=True  # 保持弹性宽度
        )
    
    def create_format_chip(self, format_name):
        """创建格式标签"""
        return ft.Container(
            content=ft.Text(
                format_name,
                size=12,
                color=ft.Colors.BLUE_700,
                weight=ft.FontWeight.BOLD
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            margin=ft.margin.all(2),
            bgcolor=ft.Colors.BLUE_100,
            border_radius=20,
        )
    
    def init_ui(self):
        """初始化用户界面"""
        # 初始化性能管理器
        if PerformanceManager:
            self.performance_manager = PerformanceManager(self.page)
        
        # 顶部导航栏
        header = self.create_header()
        
        # 主内容区域
        main_content = self.create_main_content()
        
        # 底部信息栏
        footer_content = ft.Column([
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.ROCKET_LAUNCH, size=16, color=ft.Colors.BLUE_600),
                        ft.Text("准备就绪，选择文件开始转换", color=ft.Colors.GREY_600)
                    ], spacing=4),
                    ft.Row([
                        ft.Text("版本 v2.0.0", size=12, color=ft.Colors.GREY_500),
                        ft.Text("•", size=12, color=ft.Colors.GREY_300),
                        ft.Text("公众号：AI康康老师", size=12, color=ft.Colors.BLUE_600),
                        ft.Text("•", size=12, color=ft.Colors.GREY_300),
                        ft.Text("Powered by MarkItDown", size=12, color=ft.Colors.GREY_400)
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(horizontal=20, vertical=8)
            )
        ], spacing=0)
        
        # 主布局
        self.page.add(
            ft.Column([
                header,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                main_content,
                footer_content
            ], spacing=0, expand=True)
        )
    
    def create_header(self):
        """创建顶部导航栏"""
        return ft.Container(
            content=ft.Row([
                # Logo和标题
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=32, color=ft.Colors.BLUE_600),
                    ft.Column([
                        ft.Text(
                            "MarkItDown 智能转换器",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800
                        ),
                        ft.Text(
                            "将任何文档转换为 Markdown",
                            size=12,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=0)
                ], spacing=12),
                
                # 功能状态指示器
                ft.Row([
                    self.create_status_indicator("基础转换", True, ft.Colors.GREEN),
                    self.create_status_indicator("PDF增强", self.check_pdf_support(), ft.Colors.ORANGE),
                    self.create_status_indicator("音频转录", self.check_audio_support(), ft.Colors.PURPLE),
                ], spacing=8),
                
                # 设置按钮
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        tooltip="设置",
                        on_click=self.show_settings_dialog,
                        icon_color=ft.Colors.GREY_600
                    ),
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="帮助",
                        on_click=self.show_help_dialog,
                        icon_color=ft.Colors.GREY_600
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=ft.Colors.WHITE,
        )
    
    def create_status_indicator(self, name, enabled, color):
        """创建状态指示器"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=8,
                    height=8,
                    bgcolor=color if enabled else ft.Colors.GREY_300,
                    border_radius=4
                ),
                ft.Text(
                    name,
                    size=12,
                    color=ft.Colors.GREY_700 if enabled else ft.Colors.GREY_400,
                    weight=ft.FontWeight.BOLD
                )
            ], spacing=6, tight=True),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            bgcolor=ft.Colors.GREY_50,
            border_radius=20,
        )
    
    def create_main_content(self):
        """创建主内容区域"""
        # 根据屏幕大小决定布局方向
        if hasattr(self, 'is_mobile_layout') and self.is_mobile_layout:
            # 小屏幕：垂直布局，重点突出文件列表和结果预览
            return ft.Container(
                content=ft.Column([
                    # 文件选择面板 - 紧凑但功能完整
                    ft.Container(
                        content=self.create_left_panel_compact(),
                        height=360,  # 适中高度
                    ),
                    ft.Container(height=8),
                    # 结果显示面板 - 重点区域，占据更多空间
                    ft.Container(
                        content=self.create_right_panel_compact(),
                        expand=True  # 占据剩余所有空间
                    )
                ], spacing=0, expand=True),
                padding=ft.padding.all(16),
                expand=True
            )
        else:
            # 大屏幕：水平布局
            return ft.Container(
                content=ft.Row([
                    # 左侧面板 - 文件选择和操作
                    ft.Container(
                        content=self.create_left_panel(),
                        expand=1,
                        width=None
                    ),
                    
                    # 右侧面板 - 结果显示
                    ft.Container(
                        content=self.create_right_panel(),
                        expand=2,
                        width=None
                    )
                ], spacing=16, expand=True),
                padding=ft.padding.all(24),
                expand=True
            )
    
    def create_left_panel_compact(self):
        """创建紧凑左侧面板 - 小屏幕布局"""
        # 如果还没有创建文件列表容器，创建一个
        if not hasattr(self, 'file_list_container'):
            self.file_list_container = ft.Container(
                content=self.get_file_list_content(),
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREY_200),
                bgcolor=ft.Colors.WHITE,
                padding=8,
                height=200,  # 固定高度适合紧凑布局
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=1,
                    color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    offset=ft.Offset(0, 1)
                )
            )
        
        return ft.Column([
            # 头部操作区域
            ft.Row([
                ft.Text(
                    "📁 文件选择",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=16),
                            ft.Text("选择", size=12)
                        ], spacing=4),
                        height=32,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=self.pick_files
                    ),
                    ft.TextButton(
                        "清空",
                        icon=ft.Icons.CLEAR_ALL,
                        on_click=self.clear_files,
                        style=ft.ButtonStyle(
                            color=ft.Colors.GREY_600,
                            overlay_color=ft.Colors.GREY_100
                        )
                    )
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=8),
            
            # 拖拽上传区域 - 紧凑版
            ft.Container(
                content=self.drag_area.content,
                height=120,  # 减小高度适应紧凑布局
                border_radius=12,
                border=ft.border.all(2, ft.Colors.BLUE_200),
                bgcolor=ft.Colors.BLUE_50,
                padding=12,
                on_click=self.pick_files,
                ink=True
            ),
            
            ft.Container(height=12),
            
            # 文件列表区域 - 紧凑版
            ft.Row([
                ft.Text(
                    "📋 已选择",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.GREY_700
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.TRANSFORM, size=16),
                        ft.Text("转换", size=12, weight=ft.FontWeight.W_600)
                    ], spacing=4),
                    height=32,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        elevation=1
                    ),
                    on_click=self.start_conversion
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=8),
            
            # 文件列表 - 使用共享的容器引用
            self.file_list_container
        ], spacing=0)
    
    def create_left_panel(self):
        """创建左侧面板 - 大屏幕布局"""
        # 创建文件列表容器并保存引用
        if not hasattr(self, 'file_list_container'):
            self.file_list_container = ft.Container(
                content=self.get_file_list_content(),
                border_radius=12,
                border=ft.border.all(1, ft.Colors.GREY_200),
                bgcolor=ft.Colors.WHITE,
                padding=12,
                expand=True,  # 使用弹性高度占据剩余空间
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=2,
                    color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    offset=ft.Offset(0, 1)
                )
            )
        
        return ft.Column([
            # 标题和选择文件按钮
            ft.Row([
                ft.Text(
                    "📁 文件选择",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=18),
                        ft.Text("选择文件", size=14)
                    ], spacing=6),
                    height=40,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=self.pick_files
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=12),
            
            # 支持格式提示
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_600),
                        ft.Text(
                            "支持的文件格式",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700
                        )
                    ], spacing=6),
                    ft.Container(height=6),
                    ft.Row([
                        self.create_format_chip("PDF"),
                        self.create_format_chip("DOCX"),
                        self.create_format_chip("XLSX"),
                        self.create_format_chip("PPTX"),
                        self.create_format_chip("TXT"),
                        self.create_format_chip("HTML"),
                        self.create_format_chip("图片"),
                        self.create_format_chip("音频"),
                    ], alignment=ft.MainAxisAlignment.START, wrap=True),
                ], spacing=0),
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.BLUE_200)
            ),
                
                ft.Container(height=16),
                
                # 文件列表标题和操作
                ft.Row([
                    ft.Text(
                        "📋 选中的文件",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700
                    ),
                        ft.TextButton(
                            "清空",
                            icon=ft.Icons.CLEAR_ALL,
                            on_click=self.clear_files,
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_600,
                                overlay_color=ft.Colors.GREY_100
                            )
                        )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=8),
                
            # 文件列表 - 使用保存的容器引用
            self.file_list_container,
                
                ft.Container(height=16),
                
                # 转换按钮
            ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TRANSFORM, size=20),
                            ft.Text("开始转换", size=16, weight=ft.FontWeight.W_600)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        width=float('inf'),
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            elevation=2
                        ),
                        on_click=self.start_conversion
                )
        ], spacing=0, expand=True)
    
    def create_right_panel(self):
        """创建右侧面板"""
        return ft.Container(
            content=ft.Column([
                # 标题和操作按钮
                ft.Row([
                    ft.Text(
                        "📄 转换结果",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800
                    ),
                    ft.Row([
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.COPY, size=16),
                                ft.Text("复制", size=14)
                            ], spacing=4),
                            on_click=self.copy_result,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, ft.Colors.GREY_300)
                            )
                        ),
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DOWNLOAD, size=16),
                                ft.Text("保存", size=14)
                            ], spacing=4),
                            on_click=self.save_result,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, ft.Colors.GREY_300)
                            )
                        )
                    ], spacing=8)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=12),
                
                # 结果显示区域
                ft.Container(
                    content=self.result_text,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    bgcolor=ft.Colors.WHITE,
                    padding=16,
                    expand=True,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 2)
                    )
                )
            ], expand=True),
            expand=True
        )
    
    def create_right_panel_compact(self):
        """创建紧凑版右侧面板（用于小屏幕）"""
        return ft.Column([
            # 标题和操作按钮
            ft.Row([
                ft.Text(
                    "📄 转换结果",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800
                ),
                ft.Row([
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.COPY, size=14),
                            ft.Text("复制", size=12)
                        ], spacing=3),
                        on_click=self.copy_result,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                            side=ft.BorderSide(1, ft.Colors.GREY_300)
                        )
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DOWNLOAD, size=14),
                            ft.Text("保存", size=12)
                        ], spacing=3),
                        on_click=self.save_result,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                            side=ft.BorderSide(1, ft.Colors.GREY_300)
                        )
                    )
                ], spacing=6)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=8),
            
            # 结果显示区域 - 扩大显示区域
            ft.Container(
                content=self.result_text,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_200),
                bgcolor=ft.Colors.WHITE,
                padding=16,
                expand=True,  # 使用弹性高度占满剩余空间
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2)
                )
            )
        ], spacing=0, expand=True)  # 整个面板使用弹性高度
    
    def create_footer(self):
        """创建底部状态栏"""
        return ft.Container(
            content=ft.Column([
                self.progress_bar,
                ft.Row([
                    self.status_text,
                    ft.Row([
                        ft.Text(
                            f"版本 1.0.0",
                            size=12,
                            color=ft.Colors.GREY_500
                        ),
                        ft.Text(
                            "•",
                            size=12,
                            color=ft.Colors.GREY_300
                        ),
                        ft.Text(
                            "Powered by MarkItDown",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ], spacing=8)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_200))
        )
    
    def check_pdf_support(self):
        """检查PDF支持"""
        try:
            import fitz  # PyMuPDF
            return True
        except ImportError:
            return False
    
    def check_audio_support(self):
        """检查音频转录支持"""
        try:
            import speech_recognition
            return True
        except ImportError:
            return False
    
    def init_converter(self):
        """初始化转换器"""
        try:
            # 加载API配置
            api_config = self.load_api_config()
            
            # 检查所有API配置（国际和国内）
            has_international_api = bool(
                api_config.get('openai_api_key') or 
                api_config.get('azure_endpoint')
            )
            
            has_domestic_api = bool(
                api_config.get('baidu_api_key') or
                api_config.get('qwen_api_key') or
                api_config.get('zhipu_api_key') or
                api_config.get('tencent_secret_id') or
                api_config.get('aliyun_access_key_id') or
                api_config.get('xunfei_app_id')
            )
            
            # 根据配置创建转换器
            if has_international_api or has_domestic_api:
                # 配置了API服务的增强模式
                converter_kwargs = {}
                api_types_configured = []
                
                # 配置OpenAI客户端
                if api_config.get('openai_api_key'):
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=api_config['openai_api_key'])
                        converter_kwargs['llm_client'] = client
                        converter_kwargs['llm_model'] = api_config.get('openai_model', 'gpt-4o')
                        api_types_configured.append("OpenAI")
                        logger.info("OpenAI客户端配置成功")
                    except ImportError:
                        logger.warning("OpenAI库未安装，跳过OpenAI配置")
                    except Exception as e:
                        logger.warning(f"OpenAI配置失败: {e}")
                
                # 配置Azure Document Intelligence
                if api_config.get('azure_endpoint'):
                    try:
                        from azure.core.credentials import AzureKeyCredential
                        # 使用API Key而不是DefaultAzureCredential
                        if api_config.get('azure_key'):
                            converter_kwargs['docintel_endpoint'] = api_config['azure_endpoint']
                            converter_kwargs['docintel_credential'] = AzureKeyCredential(api_config['azure_key'])
                            api_types_configured.append("Azure")
                            logger.info("Azure Document Intelligence配置成功 (API Key)")
                        else:
                            logger.warning("Azure Endpoint配置但缺少API Key")
                    except ImportError:
                        logger.warning("Azure库未安装，跳过Azure配置")
                    except Exception as e:
                        logger.warning(f"Azure配置失败: {e}")
                
                # 记录国内API配置状态（即使MarkItDown不原生支持）
                if has_domestic_api:
                    domestic_apis = []
                    if api_config.get('baidu_api_key'): domestic_apis.append("百度")
                    if api_config.get('qwen_api_key'): domestic_apis.append("通义千问")
                    if api_config.get('zhipu_api_key'): domestic_apis.append("智谱AI")
                    if api_config.get('tencent_secret_id'): domestic_apis.append("腾讯云")
                    if api_config.get('aliyun_access_key_id'): domestic_apis.append("阿里云")
                    if api_config.get('xunfei_app_id'): domestic_apis.append("讯飞")
                    
                    logger.warning(f"检测到国内API配置: {', '.join(domestic_apis)}")
                    logger.warning("注意：MarkItDown原生不支持国内API，这些配置当前不会生效")
                    logger.warning("建议使用Azure或OpenAI获得最佳转换效果")
                
                self.converter = MarkItDown(**converter_kwargs)
                
                if api_types_configured:
                    logger.info(f"转换器初始化成功（增强模式: {', '.join(api_types_configured)}）")
                else:
                    logger.info("转换器初始化成功（基础模式 - 配置的API未生效）")
            else:
                # 基础模式
                self.converter = MarkItDown()
                logger.info("转换器初始化成功（基础模式）")
                
        except Exception as e:
            logger.error(f"转换器初始化失败: {e}")
            # 回退到基础模式
            try:
                self.converter = MarkItDown()
                logger.info("回退到基础模式")
            except Exception as fallback_error:
                logger.error(f"基础模式初始化也失败: {fallback_error}")
                # 确保converter不为None
                self.converter = None
            self.show_error_snackbar("转换器初始化失败")
    
    def load_api_config(self):
        """加载API配置"""
        try:
            # 使用和设置页面相同的加载逻辑
            from src.ui.settings_page import SettingsPage
            settings = SettingsPage.load_settings()
            api_config = settings.get('api_config', {})
            
            # 记录加载到的API配置
            if api_config:
                configured_apis = [key for key, value in api_config.items() if value]
                if configured_apis:
                    logger.info(f"已加载API配置: {', '.join(configured_apis)}")
                else:
                    logger.info("未发现已配置的API")
            else:
                logger.info("未找到API配置")
            
            return api_config
        except Exception as e:
            logger.warning(f"加载API配置失败: {e}")
        
        return {}
    
    def pick_files(self, e):
        """选择文件"""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files:
                for file in e.files:
                    self.add_file_to_list(file.path)
                self.update_drag_area()
        
        file_picker = ft.FilePicker(on_result=file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=[
                "pdf", "docx", "xlsx", "pptx", "txt", 
                "jpg", "jpeg", "png", "mp3", "wav", "html"
            ]
        )
    
    def add_file_to_list(self, file_path):
        """添加文件到列表"""
        if file_path in self.selected_files:
            return
            
        # 检查文件大小限制
        file_size = self.get_file_size_mb(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # 从设置中获取文件大小限制
        from src.ui.settings_page import SettingsPage
        settings = SettingsPage.load_settings()
        size_limit_mb = settings.get('file_size_limit_mb', 100)
        
        # 应用文件大小限制
        if file_size > size_limit_mb:
            self.show_error_snackbar(f"文件过大：{file_size:.1f}MB > 限制{size_limit_mb}MB")
            return
            
        self.selected_files.append(file_path)
        file_name = Path(file_path).name
        
        # 创建文件项
        file_item = ft.Container(
            content=ft.Row([
                # 文件图标
                ft.Container(
                    content=ft.Icon(
                        self.get_file_icon(file_ext),
                        size=24,
                        color=self.get_file_color(file_ext)
                    ),
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.with_opacity(0.1, self.get_file_color(file_ext)),
                    border_radius=8,
                    alignment=ft.alignment.center
                ),
                
                # 文件信息
                ft.Column([
                    ft.Text(
                        file_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=1
                    ),
                    ft.Row([
                    ft.Text(
                        f"{file_size:.1f} MB • {file_ext.upper()}",
                        size=12,
                        color=ft.Colors.GREY_500
                        ),
                        # 转换状态指示器
                        ft.Container(
                            content=ft.Text("", size=10),
                            key=f"status_{file_path}"  # 用于后续更新状态
                    )
                    ], spacing=8)
                ], spacing=2, expand=True),
                
                # 操作按钮
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_size=20,
                        tooltip="查看结果",
                        icon_color=ft.Colors.BLUE_600,
                        on_click=lambda e, fp=file_path: self.select_file_to_view(fp)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW,
                        icon_size=20,
                        tooltip="单独转换",
                        icon_color=ft.Colors.GREEN_600,
                        on_click=lambda e, fp=file_path: self.convert_single_file(fp)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=20,
                        tooltip="移除",
                        icon_color=ft.Colors.RED_600,
                        on_click=lambda e, fp=file_path: self.remove_file_from_list(fp)
                    )
                ], spacing=0)
            ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(12),
            margin=ft.margin.only(bottom=8),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
            key=f"file_item_{file_path}",
            on_click=lambda e, fp=file_path: self.select_file_to_view(fp),  # 整个容器都可点击
            ink=True  # 添加点击反馈效果
        )
        
        self.file_list_view.controls.append(file_item)
        self.refresh_file_list_display()
        self.page.update()
    
    def remove_file_from_list(self, file_path):
        """从列表移除文件"""
        if file_path in self.selected_files:
            index = self.selected_files.index(file_path)
            self.selected_files.remove(file_path)
            self.file_list_view.controls.pop(index)
            
            # 如果删除的是当前选中的文件，清空显示
            if self.current_selected_file == file_path:
                self.current_selected_file = None
                self.result_text.value = ""
                self.update_status("📄 文件已移除", ft.Colors.GREY_600)
            
            # 移除转换结果
            if file_path in self.conversion_results:
                del self.conversion_results[file_path]
            
            self.update_drag_area()
            self.refresh_file_list_display()
            self.page.update()
    
    def clear_files(self, e):
        """清空文件列表"""
        self.selected_files.clear()
        self.file_list_view.controls.clear()
        self.conversion_results.clear()  # 同时清空转换结果
        self.current_selected_file = None  # 重置选中文件
        self.result_text.value = ""  # 清空结果显示
        self.update_drag_area()
        self.refresh_file_list_display()
        self.page.update()
    
    def update_drag_area(self):
        """更新拖拽区域显示"""
        file_count = len(self.selected_files)
        if file_count > 0:
            self.drag_area.content.controls[1].value = f"已选择 {file_count} 个文件"
            self.drag_area.content.controls[2].value = "点击添加更多文件"
        else:
            self.drag_area.content.controls[1].value = "拖拽文件到这里"
            self.drag_area.content.controls[2].value = "或点击选择文件"
        self.page.update()
    
    def get_file_size_mb(self, file_path):
        """获取文件大小（MB）"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0
    
    def get_file_icon(self, ext):
        """获取文件图标"""
        icon_map = {
            '.pdf': ft.Icons.PICTURE_AS_PDF,
            '.docx': ft.Icons.DESCRIPTION,
            '.xlsx': ft.Icons.TABLE_CHART,
            '.pptx': ft.Icons.SLIDESHOW,
            '.txt': ft.Icons.TEXT_SNIPPET,
            '.jpg': ft.Icons.IMAGE, '.jpeg': ft.Icons.IMAGE, '.png': ft.Icons.IMAGE,
            '.mp3': ft.Icons.AUDIO_FILE, '.wav': ft.Icons.AUDIO_FILE,
            '.html': ft.Icons.WEB
        }
        return icon_map.get(ext, ft.Icons.INSERT_DRIVE_FILE)
    
    def get_file_color(self, ext):
        """获取文件颜色"""
        color_map = {
            '.pdf': ft.Colors.RED_600,
            '.docx': ft.Colors.BLUE_600,
            '.xlsx': ft.Colors.GREEN_600,
            '.pptx': ft.Colors.ORANGE_600,
            '.txt': ft.Colors.GREY_600,
            '.jpg': ft.Colors.PURPLE_600, '.jpeg': ft.Colors.PURPLE_600, '.png': ft.Colors.PURPLE_600,
            '.mp3': ft.Colors.PINK_600, '.wav': ft.Colors.PINK_600,
            '.html': ft.Colors.CYAN_600
        }
        return color_map.get(ext, ft.Colors.GREY_600)
    
    def start_conversion(self, e):
        """开始批量转换"""
        if not self.selected_files:
            self.show_warning_snackbar("请先选择要转换的文件")
            return
        
        self.update_status("🚀 开始批量转换...", ft.Colors.BLUE_600)
        self.progress_bar.visible = True
        self.page.update()
        
        # 批量转换并存储结果
        total_files = len(self.selected_files)
        
        for i, file_path in enumerate(self.selected_files):
            progress = (i + 1) / total_files
            self.progress_bar.value = progress
            self.update_status(f"📄 转换中... ({i + 1}/{total_files})", ft.Colors.BLUE_600)
            self.page.update()
            
            # 转换文件并存储结果
            result = self.convert_file_internal(file_path)
            self.conversion_results[file_path] = result
        
        self.progress_bar.visible = False
        self.update_status("✅ 批量转换完成 - 点击文件查看结果", ft.Colors.GREEN_600)
        
        # 如果没有选中文件，自动选中第一个成功转换的文件
        if not self.current_selected_file:
            for file_path in self.selected_files:
                if file_path in self.conversion_results and self.conversion_results[file_path]['success']:
                    self.select_file_to_view(file_path)
                    break
        
        # 显示批量转换结果摘要
        successful = [f for f in self.selected_files if self.conversion_results.get(f, {}).get('success', False)]
        failed = [f for f in self.selected_files if not self.conversion_results.get(f, {}).get('success', False)]
        markdown_count = [f for f in successful if self.conversion_results.get(f, {}).get('is_markdown', False)]
        
        if successful and failed:
            self.show_success_snackbar(f"转换完成：{len(successful)} 成功（{len(markdown_count)} 个真正Markdown），{len(failed)} 失败")
        elif successful:
            self.show_success_snackbar(f"全部转换成功：{len(successful)} 个文件（{len(markdown_count)} 个真正Markdown）")
        else:
            self.show_error_snackbar(f"转换失败：{len(failed)} 个文件")
    
    def validate_markdown_content(self, content):
        """验证内容是否为有效的Markdown格式 - 基于CommonMark标准规范"""
        if not content or len(content.strip()) == 0:
            return False, "内容为空"
        
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # CommonMark规范中的主要特征检测
        markdown_features = {
            'headers': 0,           # ATX headers (# ## ###) 和 Setext headers (=== ---)
            'emphasis': 0,          # *italic* **bold** _italic_ __bold__
            'lists': 0,             # 有序列表和无序列表
            'code': 0,              # 内联代码`code`和代码块```
            'blockquotes': 0,       # > 引用
            'links': 0,             # [text](url) 链接
            'images': 0,            # ![alt](url) 图片
            'tables': 0,            # | | | 表格
            'horizontal_rules': 0,  # --- *** 水平分割线
            'line_breaks': 0,       # 硬换行\\或两个空格
            'html_blocks': 0,       # HTML标签
            'entity_refs': 0,       # &amp; &#123; 实体引用
            'escapes': 0            # \* \[ 反斜杠转义
        }
        
        total_checks = len(markdown_features)
        
        # 1. ATX Headers: # ## ### #### ##### ######
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') and (len(stripped) == 1 or stripped[1] in ' \t'):
                # 检查是否是有效的ATX标题（1-6个#后跟空格或制表符）
                hash_count = 0
                for char in stripped:
                    if char == '#':
                        hash_count += 1
                    else:
                        break
                if 1 <= hash_count <= 6:
                    markdown_features['headers'] += 1
                    break
        
        # 2. Setext Headers: 文本下方的 === 或 ---
        for i in range(len(lines) - 1):
            current_line = lines[i].strip()
            next_line = lines[i + 1].strip()
            if current_line and next_line:
                # 检查下一行是否全是=或-
                if (all(c == '=' for c in next_line) or all(c == '-' for c in next_line)) and len(next_line) >= 3:
                    markdown_features['headers'] += 1
                    break
        
        # 3. 强调和粗体：*text* **text** _text_ __text__
        import re
        emphasis_patterns = [
            r'\*\*[^*]+\*\*',  # **bold**
            r'__[^_]+__',      # __bold__
            r'\*[^*]+\*',      # *italic*
            r'_[^_]+_'         # _italic_
        ]
        for pattern in emphasis_patterns:
            if re.search(pattern, content):
                markdown_features['emphasis'] += 1
                break
        
        # 4. 列表：有序和无序
        for line in lines:
            stripped = line.strip()
            # 无序列表：- * +
            if re.match(r'^[-*+]\s', stripped):
                markdown_features['lists'] += 1
                break
            # 有序列表：1. 2. 3.
            if re.match(r'^\d+\.\s', stripped):
                markdown_features['lists'] += 1
                break
        
        # 5. 代码：内联`code`和代码块```
        if '`' in content:
            # 内联代码
            if re.search(r'`[^`]+`', content):
                markdown_features['code'] += 1
            # 代码块
            elif '```' in content or '~~~' in content:
                markdown_features['code'] += 1
        
        # 6. 块引用：> text
        for line in lines:
            if line.strip().startswith('>'):
                markdown_features['blockquotes'] += 1
                break
        
        # 7. 链接：[text](url) 或 [text][ref]
        link_patterns = [
            r'\[[^\]]+\]\([^)]+\)',  # [text](url)
            r'\[[^\]]+\]\[[^\]]*\]'  # [text][ref]
        ]
        for pattern in link_patterns:
            if re.search(pattern, content):
                markdown_features['links'] += 1
                break
        
        # 8. 图片：![alt](url)
        if re.search(r'!\[[^\]]*\]\([^)]+\)', content):
            markdown_features['images'] += 1
        
        # 9. 表格：| col1 | col2 |
        table_lines = [line for line in lines if '|' in line and line.strip().startswith('|')]
        if len(table_lines) >= 2:
            # 检查是否有表格分隔符行（包含 --- 的行）
            for line in table_lines:
                if '---' in line or '===' in line:
                    markdown_features['tables'] += 1
                    break
        
        # 10. 水平分割线：--- *** ___
        for line in lines:
            stripped = line.strip()
            if len(stripped) >= 3:
                if (all(c == '-' for c in stripped) or 
                    all(c == '*' for c in stripped) or 
                    all(c == '_' for c in stripped)):
                    markdown_features['horizontal_rules'] += 1
                    break
        
        # 11. 硬换行：行末两个空格或反斜杠
        for line in lines:
            if line.endswith('  ') or line.endswith('\\'):
                markdown_features['line_breaks'] += 1
                break
        
        # 12. HTML块：<tag> 标签
        html_patterns = [
            r'<[a-zA-Z][^>]*>',     # 开始标签
            r'</[a-zA-Z][^>]*>',    # 结束标签
            r'<!--.*?-->',          # 注释
            r'<![A-Z].*?>'          # DOCTYPE等声明
        ]
        for pattern in html_patterns:
            if re.search(pattern, content, re.DOTALL):
                markdown_features['html_blocks'] += 1
                break
        
        # 13. 实体引用：&amp; &#123; &#x1F;
        entity_patterns = [
            r'&[a-zA-Z][a-zA-Z0-9]*;',  # 命名实体
            r'&#\d+;',                   # 十进制数字实体
            r'&#x[0-9a-fA-F]+;'         # 十六进制数字实体
        ]
        for pattern in entity_patterns:
            if re.search(pattern, content):
                markdown_features['entity_refs'] += 1
                break
        
        # 14. 反斜杠转义：\* \[ \( 等
        if re.search(r'\\[!\"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]', content):
            markdown_features['escapes'] += 1
        
        # 计算检测到的特征数量
        detected_features = sum(1 for count in markdown_features.values() if count > 0)
        markdown_percentage = (detected_features / total_checks) * 100
        
        # 构建特征详情
        feature_details = []
        if markdown_features['headers']:
            feature_details.append("标题")
        if markdown_features['emphasis']:
            feature_details.append("强调")
        if markdown_features['lists']:
            feature_details.append("列表")
        if markdown_features['code']:
            feature_details.append("代码")
        if markdown_features['blockquotes']:
            feature_details.append("引用")
        if markdown_features['links']:
            feature_details.append("链接")
        if markdown_features['images']:
            feature_details.append("图片")
        if markdown_features['tables']:
            feature_details.append("表格")
        if markdown_features['horizontal_rules']:
            feature_details.append("分割线")
        if markdown_features['line_breaks']:
            feature_details.append("换行")
        if markdown_features['html_blocks']:
            feature_details.append("HTML")
        if markdown_features['entity_refs']:
            feature_details.append("实体")
        if markdown_features['escapes']:
            feature_details.append("转义")
        
        # 判断是否为有效Markdown
        # 宽松标准：有任何Markdown特征或结构化内容
        if detected_features >= 1:
            is_valid = True
            status = "标准Markdown"
        elif len(non_empty_lines) > 1:
            # 多行结构化文本也认为是有效的
            is_valid = True
            status = "结构化文本"
            feature_details = ["多行文本"]
        else:
            # 单行文本也可能有价值
            is_valid = True
            status = "纯文本"
            feature_details = ["基础文本"]
        
        # 构建详细说明
        if feature_details:
            detail_str = f"特征: {', '.join(feature_details)}"
        else:
            detail_str = "基础文本内容"
            
        return is_valid, f"{status} | {detail_str} | 符合度: {markdown_percentage:.1f}%"
    
    def convert_single_file(self, file_path):
        """转换单个文件"""
        self.update_status(f"📄 正在转换: {Path(file_path).name}", ft.Colors.BLUE_600)
        self.progress_bar.visible = True
        self.progress_bar.value = None  # 不确定进度
        self.page.update()
        
        # 转换并存储结果
        result = self.convert_file_internal(file_path)
        self.conversion_results[file_path] = result
        
        # 自动选中并显示这个文件的结果
        self.select_file_to_view(file_path)
        
        if result['success']:
            self.show_success_snackbar("文件转换成功！")
        else:
            self.show_error_snackbar("文件转换失败")
        
        self.progress_bar.visible = False
    
    def get_detailed_api_status(self):
        """获取详细的API状态信息"""
        api_config = self.load_api_config()
        
        status = {
            'has_international_api': False,
            'has_domestic_api': False,
            'azure_configured': False,
            'openai_configured': False,
            'domestic_apis': [],
            'api_called': False,
            'api_call_failed': False,
            'api_error': None
        }
        
        # 检查国际API
        if api_config.get('azure_endpoint') and api_config.get('azure_key'):
            status['azure_configured'] = True
            status['has_international_api'] = True
            
        if api_config.get('openai_api_key'):
            status['openai_configured'] = True
            status['has_international_api'] = True
        
        # 检查国内API
        domestic_apis = []
        if api_config.get('baidu_api_key'): domestic_apis.append('百度')
        if api_config.get('qwen_api_key'): domestic_apis.append('通义千问')
        if api_config.get('zhipu_api_key'): domestic_apis.append('智谱AI')
        if api_config.get('tencent_secret_id'): domestic_apis.append('腾讯云')
        if api_config.get('aliyun_access_key_id'): domestic_apis.append('阿里云')
        if api_config.get('xunfei_app_id'): domestic_apis.append('讯飞')
        
        if domestic_apis:
            status['has_domestic_api'] = True
            status['domestic_apis'] = domestic_apis
        
        return status

    def show_detailed_conversion_error(self, error_msg, api_status, file_path):
        """显示详细的转换错误信息"""
        file_name = Path(file_path).name
        
        # 构建详细错误信息
        error_parts = [f"📄 文件: {file_name}"]
        
        # API状态信息
        if api_status.get('has_international_api'):
            api_info = []
            if api_status.get('azure_configured'): api_info.append("Azure")
            if api_status.get('openai_configured'): api_info.append("OpenAI")
            error_parts.append(f"🚀 API状态: 增强模式 ({', '.join(api_info)})")
            
            # API调用结果
            if api_status.get('api_call_failed'):
                error_parts.append(f"❌ API调用失败: {api_status.get('api_error', '未知错误')}")
            elif api_status.get('api_called'):
                error_parts.append("✅ API调用成功但未能提取内容")
            else:
                error_parts.append("⚠️ 未调用API (可能是文件格式问题)")
        else:
            error_parts.append("📄 API状态: 基础模式")
            if api_status.get('has_domestic_api'):
                domestic_apis = api_status.get('domestic_apis', [])
                error_parts.append(f"⚠️ 国内API已配置但未生效: {', '.join(domestic_apis)}")
        
        # 原始错误信息
        error_parts.append(f"❌ 错误详情: {error_msg}")
        
        # 建议信息
        suggestions = []
        if not api_status.get('has_international_api'):
            suggestions.append("💡 建议配置Azure或OpenAI提升转换质量")
        if api_status.get('api_call_failed'):
            suggestions.append("🔧 请检查API配置和网络连接")
        if "扫描版PDF" in error_msg:
            suggestions.append("📷 扫描版PDF建议使用Azure Document Intelligence")
        
        if suggestions:
            error_parts.extend(suggestions)
        
        # 显示完整错误信息
        detailed_message = "\n".join(error_parts)
        
        # 更新UI显示
        if hasattr(self, 'result_text'):
            self.result_text.value = detailed_message
            self.result_text.color = ft.Colors.RED_600
            self.page.update()
        
        # 显示snackbar
        self.show_error_snackbar(f"转换失败: {file_name}")
        
        # 记录到日志
        logger.error(f"详细转换错误: {detailed_message.replace('\n', ' | ')}")
    
    def convert_file_internal(self, file_path):
        """内部转换方法"""
        api_status = self.get_detailed_api_status()
        
        try:
            # 记录转换开始
            file_name = Path(file_path).name
            if api_status['has_international_api']:
                active_apis = []
                if api_status['azure_configured']: active_apis.append('Azure')
                if api_status['openai_configured']: active_apis.append('OpenAI')
                logger.info(f"开始转换 {file_name} (增强模式: {', '.join(active_apis)})")
            else:
                logger.info(f"开始转换 {file_name} (基础模式)")
                if api_status['has_domestic_api']:
                    logger.warning(f"检测到国内API配置但未生效: {', '.join(api_status['domestic_apis'])}")
            
            # 执行转换
            api_status['api_called'] = api_status['has_international_api']
            
            # 检查转换器是否已正确初始化
            if self.converter is None:
                raise Exception("转换器未能正确初始化，请重启程序或检查依赖包安装")
            
            result = self.converter.convert(file_path)
            
            # 改进的内容验证
            content = result.text_content
            is_valid_content = False
            content_analysis = ""
            
            if content and len(content.strip()) > 0:
                # 详细质量分析
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                words = content.split()
                content_length = len(content.strip())
                
                # 质量评分
                quality_score = 0
                
                # 长度评分 (0-2分)
                if content_length > 100: quality_score += 2
                elif content_length > 30: quality_score += 1
                
                # 行数评分 (0-2分)
                if len(non_empty_lines) > 5: quality_score += 2
                elif len(non_empty_lines) > 2: quality_score += 1
                
                # 单词数评分 (0-2分)
                if len(words) > 20: quality_score += 2
                elif len(words) > 8: quality_score += 1
                
                # 特殊情况检查
                is_only_numbers = content.strip().replace(' ', '').replace('\n', '').isdigit()
                is_repetitive = len(set(content.replace(' ', '').replace('\n', ''))) < 5
                
                # 最终判断 - 更宽松的标准
                if quality_score >= 3 and not is_only_numbers and not is_repetitive:
                    is_valid_content = True
                    content_analysis = f"内容质量良好 (评分: {quality_score}/6)"
                elif quality_score >= 1 and not is_only_numbers:
                    is_valid_content = True
                    content_analysis = f"内容质量可接受 (评分: {quality_score}/6)"
                else:
                    content_analysis = f"内容质量不足 (评分: {quality_score}/6)"
            
            if is_valid_content:
                # 验证是否为真正的Markdown格式
                is_markdown, validation_msg = self.validate_markdown_content(result.text_content)
                
                # 记录成功的转换到历史记录
                self.history_manager.add_conversion(
                    files=[file_path],
                    output_file="",
                    success=True,
                    char_count=len(result.text_content)
                )
                
                # 添加到最近文件列表
                self.recent_files_manager.add_recent_file(file_path, success=True)
                
                # 成功消息
                success_msg = f"✅ 转换成功: {file_name}"
                if api_status['api_called']:
                    success_msg += " (已使用AI增强)"
                logger.info(success_msg)
                
                return {
                    'success': True,
                    'content': result.text_content,
                    'char_count': len(result.text_content),
                    'file_path': file_path,
                    'is_markdown': is_markdown,
                    'validation_msg': validation_msg,
                    'api_used': api_status['has_international_api'],
                    'api_mode': "API增强模式" if api_status['has_international_api'] else "基础模式"
                }
            else:
                # 转换失败 - 内容为空
                error_msg = "未能提取到内容，可能是扫描版PDF或图片质量问题"
                self.show_detailed_conversion_error(error_msg, api_status, file_path)
                
                # 记录失败的转换到历史记录
                self.history_manager.add_conversion(
                    files=[file_path],
                    output_file="",
                    success=False,
                    error_msg=error_msg
                )
                
                # 添加到最近文件列表（标记为失败）
                self.recent_files_manager.add_recent_file(file_path, success=False)
                
                return {
                    'success': False,
                    'error': error_msg,
                    'file_path': file_path,
                    'is_markdown': False,
                    'validation_msg': "转换失败"
                }
                
        except Exception as e:
            # 记录异常到历史记录
            error_msg = str(e)
            logger.error(f"转换过程出错: {e}")
            api_status['conversion_error'] = error_msg
            self.show_detailed_conversion_error(error_msg, api_status, file_path)
            
            self.history_manager.add_conversion(
                files=[file_path],
                output_file="",
                success=False,
                error_msg=error_msg
            )
            
            # 添加到最近文件列表（标记为失败）
            self.recent_files_manager.add_recent_file(file_path, success=False)
            
            return {
                'success': False,
                'error': error_msg,
                'file_path': file_path,
                'is_markdown': False,
                'validation_msg': "转换异常"
            }
    
    def select_file_to_view(self, file_path):
        """选择文件查看转换结果"""
        # 更新当前选中文件
        old_selected = self.current_selected_file
        self.current_selected_file = file_path
        
        # 更新界面选中状态
        self.update_file_selection_ui(old_selected, file_path)
        
        # 显示该文件的转换结果
        if file_path in self.conversion_results:
            result = self.conversion_results[file_path]
            if result['success']:
                # 显示转换内容
                self.result_text.value = result['content']
                
                # 显示验证信息 - 基于官方MarkItDown标准
                validation_info = result.get('validation_msg', '')
                if result.get('is_markdown', False):
                    if "有效Markdown" in validation_info:
                        status_icon = "✅"
                        status_color = ft.Colors.GREEN_600
                    elif "结构化文本" in validation_info:
                        status_icon = "📄"
                        status_color = ft.Colors.BLUE_600
                    else:
                        status_icon = "📝"
                        status_color = ft.Colors.GREY_700
                else:
                    status_icon = "❌"
                    status_color = ft.Colors.RED_600
                
                # 添加API使用状态显示
                api_info = result.get('api_mode', '未知模式')
                api_indicator = "🚀" if result.get('api_used', False) else "🔧"
                
                self.update_status(
                    f"{status_icon} {Path(file_path).name} | {validation_info} | {api_indicator} {api_info} ({result['char_count']} 字符)", 
                    status_color
                )
            else:
                self.result_text.value = f"❌ 转换失败\n\n{result['error']}"
                self.update_status(f"❌ 失败: {Path(file_path).name}", ft.Colors.RED_600)
        else:
            # 如果还没有转换结果，显示提示
            self.result_text.value = f"📄 {Path(file_path).name}\n\n⏳ 尚未转换此文件\n\n点击 ▶️ 按钮开始转换，或使用批量转换功能。"
            self.update_status(f"📄 选中: {Path(file_path).name} (未转换)", ft.Colors.GREY_600)
        
        self.page.update()

    def update_file_selection_ui(self, old_file, new_file):
        """更新文件选中状态的UI"""
        # 简化选中状态更新逻辑
        for i, file_path in enumerate(self.selected_files):
            if i < len(self.file_list_view.controls):
                container = self.file_list_view.controls[i]
                if hasattr(container, 'bgcolor') and hasattr(container, 'border'):
                    if file_path == new_file:
                        # 选中状态
                        container.bgcolor = ft.Colors.BLUE_50
                        container.border = ft.border.all(2, ft.Colors.BLUE_400)
                    else:
                        # 未选中状态
                        container.bgcolor = ft.Colors.GREY_50
                        container.border = ft.border.all(1, ft.Colors.GREY_200)
        self.page.update()

    def update_file_status_indicator(self, file_path, status):
        """更新文件转换状态指示器"""
        # 简化状态指示器更新 - 暂时不实现复杂的UI更新
        pass  # 可以在将来扩展这个功能
    
    def copy_result(self, e):
        """复制结果"""
        if self.result_text.value:
            self.page.set_clipboard(self.result_text.value)
            self.show_success_snackbar("结果已复制到剪贴板")
        else:
            self.show_warning_snackbar("没有可复制的内容")
    
    def save_result(self, e):
        """保存结果"""
        if not self.result_text.value:
            self.show_warning_snackbar("没有可保存的内容")
            return
        
        # 从设置中获取默认保存格式
        from src.ui.settings_page import SettingsPage
        settings = SettingsPage.load_settings()
        default_format = settings.get('default_format', 'markdown')
        
        # 根据格式设置文件名和扩展名
        if default_format == 'text':
            default_filename = "converted_result.txt"
            allowed_exts = ["txt", "md"]
        else:  # markdown
            default_filename = "converted_result.md"
            allowed_exts = ["md", "txt"]
        
        def save_file_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, 'w', encoding='utf-8') as f:
                        f.write(self.result_text.value)
                    self.show_success_snackbar(f"文件已保存到: {Path(e.path).name}")
                except Exception as ex:
                    self.show_error_snackbar(f"保存失败: {str(ex)}")
        
        save_file_picker = ft.FilePicker(on_result=save_file_result)
        self.page.overlay.append(save_file_picker)
        self.page.update()
        save_file_picker.save_file(
            dialog_title="保存转换结果",
            file_name=default_filename,
            allowed_extensions=allowed_exts
        )
    
    def show_settings_dialog(self, e):
        """显示设置页面（替代对话框）"""
        print("设置按钮被点击了！")
        self.switch_to_settings()
    
    def show_help_dialog(self, e):
        """显示帮助对话框"""
        # 获取历史统计信息
        stats = self.history_manager.get_statistics()
        recent_history = self.history_manager.get_recent_history(limit=5)
        recent_files = self.recent_files_manager.get_recent_files()
        
        help_content = ft.Column([
            ft.Text("📖 使用指南", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # 添加转换统计信息
            ft.ExpansionTile(
                title=ft.Text("📊 转换统计"),
                controls=[
                    ft.Text(f"• 总转换次数: {stats['total_conversions']}"),
                    ft.Text(f"• 成功转换: {stats['success_conversions']}"),
                    ft.Text(f"• 成功率: {stats['success_rate']:.1f}%"),
                    ft.Text(f"• 处理文件数: {stats['total_files']}"),
                    ft.Text(f"• 总字符数: {stats['total_chars']:,}")
                ]
            ),
            
            # 添加最近转换记录
            ft.ExpansionTile(
                title=ft.Text("📝 最近转换"),
                controls=[
                    ft.Text(f"• {record['date_str']}: {record['file_count']} 个文件 {'✅' if record['success'] else '❌'}")
                    for record in recent_history[:3]
                ] if recent_history else [ft.Text("• 暂无转换记录")]
            ),
            
            ft.ExpansionTile(
                title=ft.Text("支持的文件格式"),
                controls=[
                    ft.Text("• PDF文档 (.pdf)"),
                    ft.Text("• Word文档 (.docx)"),
                    ft.Text("• Excel表格 (.xlsx)"),
                    ft.Text("• PowerPoint (.pptx)"),
                    ft.Text("• 纯文本 (.txt)"),
                    ft.Text("• 图片文件 (.jpg, .png)"),
                    ft.Text("• 音频文件 (.mp3, .wav)"),
                    ft.Text("• 网页文件 (.html)")
                ]
            ),
            
            ft.ExpansionTile(
                title=ft.Text("使用步骤"),
                controls=[
                    ft.Text("1. 拖拽文件到上传区域或点击选择"),
                    ft.Text("2. 查看文件列表确认选择"),
                    ft.Text("3. 点击'开始转换'进行批量转换"),
                    ft.Text("4. 或点击单个文件的播放按钮单独转换"),
                    ft.Text("5. 查看结果并复制或保存")
                ]
            ),
            
            ft.ExpansionTile(
                title=ft.Text("常见问题"),
                controls=[
                    ft.Text("Q: PDF转换失败怎么办？"),
                    ft.Text("A: 可能是扫描版PDF，建议启用Azure模式"),
                    ft.Text("Q: 音频转录不工作？"),
                    ft.Text("A: 需要网络连接和相关依赖包"),
                    ft.Text("Q: 文件大小限制？"),
                    ft.Text("A: 建议单个文件小于50MB")
                ]
            )
        ], spacing=8, scroll=ft.ScrollMode.AUTO)
        
        dialog = ft.AlertDialog(
            title=ft.Text("帮助"),
            content=ft.Container(content=help_content, width=450, height=500),
            actions=[ft.TextButton("确定", on_click=lambda e: self.close_dialog())]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """关闭对话框"""
        if hasattr(self.page, 'dialog') and self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            self.page.update()
            print("对话框已关闭")
    
    def update_status(self, message, color=ft.Colors.GREY_600):
        """更新状态信息"""
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()
    
    def show_success_snackbar(self, message):
        """显示成功提示"""
        snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ]),
            bgcolor=ft.Colors.GREEN_600
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()
    
    def show_error_snackbar(self, message):
        """显示错误提示"""
        snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ]),
            bgcolor=ft.Colors.RED_600
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()
    
    def show_warning_snackbar(self, message):
        """显示警告提示"""
        snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE)
            ]),
            bgcolor=ft.Colors.ORANGE_600
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()
    
    def switch_to_settings(self):
        """切换到设置页面"""
        try:
            from src.ui.settings_page import SettingsPage
            
            self.current_page = "settings"
            self.settings_page = SettingsPage(
                page=self.page,
                on_back=self.switch_to_main,
                on_settings_changed=self.on_settings_changed
            )
            
            # 清空当前页面内容
            self.page.controls.clear()
            
            # 添加设置页面内容
            self.page.add(self.settings_page.create_page_content())
            self.page.update()
            print("已切换到设置页面")
            
        except Exception as ex:
            print(f"切换到设置页面失败: {ex}")
            self.show_error_snackbar(f"打开设置失败: {str(ex)}")
    
    def switch_to_main(self):
        """切换回主页面"""
        try:
            self.current_page = "main"
            
            # 清空当前页面内容
            self.page.controls.clear()
            
            # 重新初始化主界面
            self.init_ui()
            self.page.update()
            print("已切换回主页面")
            
        except Exception as ex:
            print(f"切换回主页面失败: {ex}")
    
    def on_settings_changed(self, settings_data):
        """处理设置变更"""
        try:
            # 更新配置
            self.config.update(settings_data)
            self.save_config()
            
            # 检查是否有API配置变更
            has_api_changes = any(key.startswith(('openai_', 'azure_', 'api_config')) for key in settings_data.keys())
            
            # 应用主题变更
            if "theme" in settings_data:
                theme_mode = settings_data["theme"]
                if theme_mode == "light":
                    self.page.theme_mode = ft.ThemeMode.LIGHT
                elif theme_mode == "dark":
                    self.page.theme_mode = ft.ThemeMode.DARK
                else:
                    self.page.theme_mode = ft.ThemeMode.SYSTEM
                self.page.update()
            
            # 如果有API配置变更，重新初始化转换器
            if has_api_changes:
                logger.info("检测到API配置变更，重新初始化转换器")
                self.init_converter()
                
                # 更新状态指示器
                self.update_converter_status()
            
            self.show_success_snackbar("设置已保存")
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            self.show_error_snackbar(f"保存设置失败: {str(e)}")
    
    def update_converter_status(self):
        """更新转换器状态显示"""
        try:
            api_config = self.load_api_config()
            has_openai = bool(api_config.get('openai_api_key'))
            has_azure = bool(api_config.get('azure_endpoint'))
            
            if has_openai or has_azure:
                self.update_status("🚀 增强模式已启用 (API配置生效)", ft.Colors.GREEN_600)
            else:
                self.update_status("📄 基础模式运行中", ft.Colors.BLUE_600)
                
        except Exception as e:
            logger.warning(f"更新状态失败: {e}")

    def on_window_resized(self, e):
        """窗口大小变化时的响应"""
        self.update_responsive_layout()
        self.page.update()

    def update_responsive_layout(self):
        """更新响应式布局"""
        window_width = self.page.window.width or 1200
        window_height = self.page.window.height or 900
        
        # 根据屏幕宽度调整布局
        old_mobile_layout = getattr(self, 'is_mobile_layout', False)
        if window_width < 1000:
            # 小屏幕：垂直布局
            self.is_mobile_layout = True
        else:
            # 大屏幕：水平布局
            self.is_mobile_layout = False
            
        # 如果布局模式发生变化，重新创建拖拽区域
        if old_mobile_layout != self.is_mobile_layout:
            self.drag_area = self.create_drag_area()

def main(page: ft.Page):
    """主函数"""
    app = BeautifulMarkItDownApp(page)

if __name__ == "__main__":
    ft.app(target=main) 