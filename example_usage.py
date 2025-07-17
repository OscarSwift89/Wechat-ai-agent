#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动运营系统 - 使用示例
"""

from login_manager import LoginManager
from publisher import Publisher
from gpt_reply import GPTReply

def example_qr_login():
    """示例：扫码登录"""
    print("=" * 50)
    print("示例：扫码登录")
    print("=" * 50)
    
    login_manager = LoginManager()
    
    # 登录所有账号
    print("1. 登录所有账号")
    results = login_manager.login_all_accounts()
    
    print("\n登录结果:")
    for account, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {account}: {status}")
    
    # 登录单个账号
    print("\n2. 登录单个账号")
    success = login_manager.login_single_account("账号1")
    print(f"  账号1: {'✅ 成功' if success else '❌ 失败'}")
    
    # 验证登录状态
    print("\n3. 验证登录状态")
    for account in login_manager.config['accounts']:
        account_name = account['name']
        is_valid = login_manager.verify_login_status(account_name)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"  {account_name}: {status}")

def example_publish():
    """示例：发布笔记"""
    print("\n" + "=" * 50)
    print("示例：发布笔记")
    print("=" * 50)
    
    publisher = Publisher()
    
    # 创建示例文案
    print("1. 创建示例文案")
    publisher.create_sample_draft()
    
    # 发布笔记
    print("\n2. 发布笔记")
    results = publisher.publish_all_drafts(max_posts=1)
    
    print("\n发布结果:")
    for key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {key}: {status}")

def example_comment():
    """示例：评论回复"""
    print("\n" + "=" * 50)
    print("示例：评论回复")
    print("=" * 50)
    
    gpt_reply = GPTReply()
    
    # 创建示例目标笔记
    print("1. 创建示例目标笔记配置")
    gpt_reply.create_sample_target_notes()
    
    # 评论回复
    print("\n2. 评论回复")
    results = gpt_reply.reply_to_target_notes()
    
    print("\n评论结果:")
    for key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {key}: {status}")

def main():
    """主函数"""
    print("小红书自动运营系统 - 使用示例")
    print("请确保已正确配置 config.yaml 文件")
    print()
    
    try:
        # 扫码登录示例
        example_qr_login()
        
        # 发布笔记示例
        example_publish()
        
        # 评论回复示例
        example_comment()
        
        print("\n" + "=" * 50)
        print("示例运行完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 