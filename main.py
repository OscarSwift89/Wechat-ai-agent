#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动运营系统主程序
支持多账号管理、自动发帖、自动评论回复
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

from login_manager import LoginManager
from publisher import Publisher
from gpt_reply import GPTReply

class XiaohongshuBot:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化小红书机器人"""
        self.config_path = config_path
        self.setup_logging()
        
        # 初始化各个模块
        self.login_manager = LoginManager(config_path)
        self.publisher = Publisher(config_path)
        self.gpt_reply = GPTReply(config_path)
        
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'bot_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def login_all_accounts(self):
        """登录所有账号"""
        self.logger.info("开始登录所有账号...")
        results = self.login_manager.login_all_accounts()
        
        print("\n登录结果:")
        for account, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{account}: {status}")
        
        return results
    
    def publish_notes(self, max_posts=None):
        """发布笔记"""
        self.logger.info("开始发布笔记...")
        results = self.publisher.publish_all_drafts(max_posts)
        
        print("\n发布结果:")
        for key, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{key}: {status}")
        
        return results
    
    def reply_comments(self, note_urls=None, max_comments=None):
        """回复评论"""
        self.logger.info("开始回复评论...")
        
        if note_urls is None:
            results = self.gpt_reply.reply_to_target_notes()
        else:
            results = self.gpt_reply.reply_to_multiple_notes(note_urls, max_comments)
        
        print("\n评论结果:")
        for key, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"{key}: {status}")
        
        return results
    
    def run_full_workflow(self):
        """运行完整工作流程"""
        self.logger.info("开始运行完整工作流程...")
        
        # 1. 登录所有账号
        print("=" * 50)
        print("步骤 1: 登录账号")
        print("=" * 50)
        login_results = self.login_all_accounts()
        
        # 检查登录结果
        successful_logins = sum(1 for success in login_results.values() if success)
        if successful_logins == 0:
            self.logger.error("没有账号登录成功，停止执行")
            return False
        
        # 2. 发布笔记
        print("\n" + "=" * 50)
        print("步骤 2: 发布笔记")
        print("=" * 50)
        publish_results = self.publish_notes()
        
        # 3. 回复评论
        print("\n" + "=" * 50)
        print("步骤 3: 回复评论")
        print("=" * 50)
        comment_results = self.reply_comments()
        
        # 4. 总结报告
        print("\n" + "=" * 50)
        print("执行总结")
        print("=" * 50)
        
        login_success = sum(1 for success in login_results.values() if success)
        publish_success = sum(1 for success in publish_results.values() if success)
        comment_success = sum(1 for success in comment_results.values() if success)
        
        print(f"登录成功: {login_success}/{len(login_results)}")
        print(f"发布成功: {publish_success}/{len(publish_results)}")
        print(f"评论成功: {comment_success}/{len(comment_results)}")
        
        return True
    
    def create_sample_files(self):
        """创建示例文件"""
        self.logger.info("创建示例文件...")
        
        # 创建示例文案
        self.publisher.create_sample_draft()
        
        # 创建示例目标笔记
        self.gpt_reply.create_sample_target_notes()
        
        print("✅ 示例文件创建完成")
        print("📁 请查看以下目录:")
        print(f"   - 文案目录: {self.publisher.drafts_dir}")
        print(f"   - 图片目录: {self.publisher.assets_dir}")
        print("📝 请编辑 config.yaml 文件配置你的账号信息")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小红书自动运营系统")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--mode", choices=["login", "publish", "comment", "full", "setup", "qr-login"], 
                       default="full", help="运行模式")
    parser.add_argument("--max-posts", type=int, help="最大发帖数量")
    parser.add_argument("--max-comments", type=int, help="最大评论数量")
    parser.add_argument("--note-urls", nargs="+", help="目标笔记链接列表")
    parser.add_argument("--account", type=str, help="指定账号名称（用于qr-login模式）")
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not Path(args.config).exists():
        print(f"❌ 配置文件 {args.config} 不存在")
        print("请先运行: python main.py --mode setup")
        return
    
    # 创建机器人实例
    bot = XiaohongshuBot(args.config)
    
    try:
        if args.mode == "setup":
            # 创建示例文件
            bot.create_sample_files()
            
        elif args.mode == "login":
            # 仅登录
            bot.login_all_accounts()
            
        elif args.mode == "qr-login":
            # 扫码登录指定账号
            if args.account:
                success = bot.login_manager.login_single_account(args.account)
                if success:
                    print(f"✅ 账号 {args.account} 登录成功")
                else:
                    print(f"❌ 账号 {args.account} 登录失败")
            else:
                print("❌ 请使用 --account 参数指定要登录的账号名称")
            
        elif args.mode == "publish":
            # 仅发布
            bot.publish_notes(args.max_posts)
            
        elif args.mode == "comment":
            # 仅评论
            bot.reply_comments(args.note_urls, args.max_comments)
            
        elif args.mode == "full":
            # 完整流程
            bot.run_full_workflow()
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        logging.error(f"执行错误: {e}", exc_info=True)

if __name__ == "__main__":
    main() 