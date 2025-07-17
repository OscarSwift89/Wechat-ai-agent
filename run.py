#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动运营系统 - 快速启动脚本
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import playwright
        import openai
        import yaml
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_playwright_browser():
    """检查Playwright浏览器是否安装"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
        print("✅ Playwright浏览器检查通过")
        return True
    except Exception as e:
        print(f"❌ Playwright浏览器未安装: {e}")
        print("请运行: playwright install chromium")
        return False

def check_config():
    """检查配置文件"""
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ 配置文件不存在")
        print("请先运行: python main.py --mode setup")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("小红书自动运营系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查Playwright浏览器
    if not check_playwright_browser():
        return
    
    # 检查配置文件
    if not check_config():
        return
    
    print("\n🚀 开始运行小红书自动运营系统...")
    print("提示: 按 Ctrl+C 可以随时中断执行")
    print("-" * 50)
    
    # 导入并运行主程序
    try:
        from main import main as run_main
        run_main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 