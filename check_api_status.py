#!/usr/bin/env python3
"""
简单的API状态检查工具
帮助用户验证API配置是否正确加载和使用
"""

import json
from pathlib import Path


def check_current_api_status():
    """检查当前API配置状态"""
    print("🔍 微软API配置状态检查")
    print("=" * 40)
    
    # 1. 检查设置文件中的API配置
    print("\n1. 📂 检查保存的API配置:")
    
    settings_locations = [
        Path("markitdown_settings.json"),
        Path.home() / ".markitdown" / "settings.json"
    ]
    
    api_config_found = False
    for settings_file in settings_locations:
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    api_config = settings.get('api_config', {})
                    
                    if api_config:
                        print(f"   ✅ 在 {settings_file} 找到API配置")
                        
                        # 检查微软相关API
                        azure_endpoint = api_config.get('azure_endpoint', '')
                        azure_key = api_config.get('azure_key', '')
                        openai_key = api_config.get('openai_api_key', '')
                        
                        print(f"   Azure端点: {'已配置' if azure_endpoint else '未配置'}")
                        print(f"   Azure Key: {'已配置' if azure_key else '未配置'}")
                        print(f"   OpenAI Key: {'已配置' if openai_key else '未配置'}")
                        
                        if azure_endpoint or azure_key or openai_key:
                            api_config_found = True
                            
                        break
                    
            except Exception as e:
                print(f"   ❌ 读取 {settings_file} 失败: {e}")
    
    if not api_config_found:
        print("   ⚠️ 未找到已配置的API")
    
    # 2. 检查应用如何识别API状态
    print("\n2. 🚀 应用启动时API状态识别:")
    print("   在运行 python main.py 时，查看控制台输出：")
    print("   ✅ '已加载API配置: azure_endpoint, azure_key' - API已加载")
    print("   ✅ 'OpenAI客户端配置成功' - OpenAI API已配置")
    print("   ✅ 'Azure Document Intelligence配置成功' - Azure API已配置")
    print("   ✅ '转换器初始化成功（增强模式）' - 使用API增强功能")
    print("   ⚠️ '转换器初始化成功（基础模式）' - 未使用API")
    
    # 3. 检查转换时的API使用状态
    print("\n3. 📄 文件转换时API使用指示:")
    print("   转换文件时，状态栏会显示：")
    print("   🚀 API增强模式 - 表示使用了微软API")
    print("   🔧 基础模式 - 表示未使用API")
    
    # 4. 提供验证建议
    print("\n" + "=" * 40)
    print("📋 如何验证API是否真正调用:")
    
    print("\n✅ 立即验证方法:")
    print("1. 重新启动应用: python main.py")
    print("2. 查看控制台输出的API配置信息")
    print("3. 上传一个文件进行转换")
    print("4. 在状态栏查看是否显示 '🚀 API增强模式'")
    
    print("\n🔧 如果显示基础模式:")
    print("1. 检查设置页面的API配置是否已保存")
    print("2. 确认API Key格式正确")
    print("3. 尝试使用设置页面的连接测试功能")
    
    # 5. 创建快速验证脚本
    create_quick_verification_script()


def create_quick_verification_script():
    """创建快速验证脚本"""
    script_content = '''#!/usr/bin/env python3
"""快速API验证脚本"""

def quick_api_check():
    try:
        # 加载设置
        from src.ui.settings_page import SettingsPage
        settings = SettingsPage.load_settings()
        api_config = settings.get('api_config', {})
        
        print("🔍 快速API状态检查:")
        print("-" * 30)
        
        # 检查配置
        azure_endpoint = api_config.get('azure_endpoint', '')
        azure_key = api_config.get('azure_key', '')
        openai_key = api_config.get('openai_api_key', '')
        
        has_api = bool(azure_endpoint or azure_key or openai_key)
        
        print(f"API配置状态: {'✅ 已配置' if has_api else '❌ 未配置'}")
        
        if has_api:
            print("配置的API服务:")
            if azure_endpoint: print(f"  • Azure端点: {azure_endpoint[:30]}...")
            if azure_key: print(f"  • Azure Key: 已配置 ({len(azure_key)} 字符)")
            if openai_key: print(f"  • OpenAI Key: 已配置 ({len(openai_key)} 字符)")
        
        return has_api
        
    except Exception as e:
        print(f"检查失败: {e}")
        return False

if __name__ == "__main__":
    quick_api_check()
'''
    
    with open("quick_api_check.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("\n📄 快速验证脚本已创建: quick_api_check.py")
    print("   运行: python quick_api_check.py")


if __name__ == "__main__":
    check_current_api_status() 