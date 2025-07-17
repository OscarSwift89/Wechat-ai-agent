#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动运营系统 - 安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}完成")
            return True
        else:
            print(f"❌ {description}失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}出错: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装Python依赖包...")
    
    # 升级pip
    if not run_command("python -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装依赖包"):
        return False
    
    return True

def install_playwright():
    """安装Playwright浏览器"""
    print("\n🌐 安装Playwright浏览器...")
    
    if not run_command("playwright install chromium", "安装Chromium浏览器"):
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建目录结构...")
    
    directories = [
        "drafts",
        "assets", 
        "cookies",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    return True

def create_sample_files():
    """创建示例文件"""
    print("\n📝 创建示例文件...")
    
    # 创建示例文案
    sample_draft = """# 小红书文案示例

这是一篇示例文案，你可以在这里写你的笔记内容。

## 主要内容
- 第一点
- 第二点  
- 第三点

## 总结
这是一个很好的分享，希望对大家有帮助！

#小红书 #示例 #分享"""
    
    with open("drafts/sample_draft.txt", "w", encoding="utf-8") as f:
        f.write(sample_draft)
    print("✅ 创建示例文案: drafts/sample_draft.txt")
    
    # 创建示例配置文件
    sample_config = """# 小红书自动运营系统配置文件

# 账号配置（扫码登录）
accounts:
  - name: "账号1"
    cookie_file: "cookies/account1_cookies.json"
  - name: "账号2"
    cookie_file: "cookies/account2_cookies.json"

# OpenAI API配置
openai:
  api_key: "your_openai_api_key"
  model: "gpt-3.5-turbo"
  max_tokens: 150
  temperature: 0.7

# 浏览器配置
browser:
  headless: false  # 设置为true可无头模式运行
  slow_mo: 1000    # 操作间隔时间(毫秒)
  timeout: 30000   # 页面加载超时时间

# 操作延迟配置(毫秒)
delays:
  page_load: 3000      # 页面加载后等待时间
  element_click: 1000   # 点击元素后等待时间
  text_input: 500      # 文本输入间隔时间
  upload_file: 2000    # 文件上传后等待时间
  comment_reply: 2000  # 评论回复后等待时间

# 文件路径配置
paths:
  drafts: "drafts/"           # 文案目录
  assets: "assets/"           # 图片目录
  cookies: "cookies/"         # Cookie存储目录
  logs: "logs/"              # 日志目录

# 发帖配置
publishing:
  max_posts_per_day: 5       # 每日最大发帖数
  min_interval_hours: 2      # 发帖最小间隔(小时)
  auto_save_draft: true      # 是否自动保存草稿

# 评论配置
commenting:
  max_comments_per_day: 20   # 每日最大评论数
  min_interval_minutes: 30   # 评论最小间隔(分钟)
  target_notes: []           # 目标笔记链接列表
  comment_templates:         # 评论模板
    - "很棒的分享！学到了很多"
    - "这个建议很实用，谢谢分享"
    - "内容很有价值，收藏了"
    - "写得很好，继续加油"
"""
    
    with open("config.yaml", "w", encoding="utf-8") as f:
        f.write(sample_config)
    print("✅ 创建配置文件: config.yaml")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("小红书自动运营系统 - 安装向导")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，请检查网络连接")
        return
    
    # 安装Playwright
    if not install_playwright():
        print("❌ Playwright安装失败")
        return
    
    # 创建目录
    if not create_directories():
        print("❌ 目录创建失败")
        return
    
    # 创建示例文件
    if not create_sample_files():
        print("❌ 示例文件创建失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 安装完成！")
    print("=" * 60)
    
    print("\n📋 下一步操作:")
    print("1. 编辑 config.yaml 文件，配置你的账号信息")
    print("2. 在 drafts/ 目录添加你的文案文件")
    print("3. 在 assets/ 目录添加对应的图片文件")
    print("4. 运行 python run.py 开始使用")
    
    print("\n📖 详细说明请查看 README.md 文件")
    print("💡 如有问题，请查看日志文件或提交Issue")

if __name__ == "__main__":
    main() 