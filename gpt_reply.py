import json
import os
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
import yaml
import logging
from datetime import datetime, timedelta
import openai
from login_manager import LoginManager

class GPTReply:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化GPT回复管理器"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.login_manager = LoginManager(config_path)
        
        # 初始化OpenAI客户端
        openai.api_key = self.config['openai']['api_key']
        
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path(self.config['paths']['logs'])
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'gpt_reply.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def random_delay(self, min_delay: int = 1000, max_delay: int = 3000):
        """随机延迟，模拟人工操作"""
        delay = random.randint(min_delay, max_delay)
        time.sleep(delay / 1000)
    
    def human_like_typing(self, page: Page, selector: str, text: str):
        """模拟人工输入文字"""
        page.click(selector)
        page.fill(selector, "")  # 清空输入框
        
        for char in text:
            page.type(selector, char)
            time.sleep(random.randint(50, 150) / 1000)  # 随机输入间隔
    
    def generate_comment_with_gpt(self, note_content: str, comment_context: str = "") -> str:
        """使用GPT生成评论内容"""
        try:
            prompt = f"""请为以下小红书笔记生成一条自然、友好的评论回复。评论应该：
1. 表达对内容的认可和感谢
2. 语言自然，符合小红书用户习惯
3. 长度控制在50字以内
4. 避免过于营销化的语言

笔记内容：{note_content}

评论上下文：{comment_context}

请直接返回评论内容，不要包含其他说明："""

            response = openai.ChatCompletion.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "你是一个小红书用户，擅长写友好、自然的评论。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['openai']['max_tokens'],
                temperature=self.config['openai']['temperature']
            )
            
            comment = response.choices[0].message.content.strip()
            self.logger.info(f"GPT生成评论: {comment}")
            return comment
            
        except Exception as e:
            self.logger.error(f"GPT生成评论失败: {e}")
            # 使用备用模板
            templates = self.config['commenting']['comment_templates']
            return random.choice(templates)
    
    def reply_to_note(self, account_name: str, note_url: str) -> bool:
        """对指定笔记进行评论回复"""
        self.logger.info(f"开始评论笔记: {note_url} (账号: {account_name})")
        
        # 加载账号Cookie
        cookies = self.login_manager.load_cookies(account_name)
        if not cookies:
            self.logger.error(f"账号 {account_name} 的Cookie不存在，请先登录")
            return False
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.config['browser']['headless'],
                slow_mo=self.config['browser']['slow_mo']
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # 添加Cookie
            context.add_cookies(cookies)
            
            page = context.new_page()
            page.set_default_timeout(self.config['browser']['timeout'])
            
            try:
                # 访问笔记页面
                page.goto(note_url)
                self.random_delay(3000, 5000)
                
                # 等待页面加载
                page.wait_for_load_state("networkidle")
                
                # 检查是否已登录
                try:
                    if "login" in page.url.lower():
                        self.logger.error(f"账号 {account_name} 登录状态已失效")
                        return False
                except:
                    pass
                
                # 获取笔记内容用于生成评论
                note_content = ""
                try:
                    content_element = page.locator('.content, .note-content, [data-testid="note-content"]').first
                    if content_element.is_visible():
                        note_content = content_element.text_content()
                except:
                    self.logger.warning("无法获取笔记内容，将使用默认模板")
                
                # 滚动到评论区
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.random_delay(2000, 4000)
                
                # 查找评论输入框
                comment_input = page.locator('textarea[placeholder*="评论"], input[placeholder*="评论"], .comment-input').first
                if not comment_input.is_visible():
                    # 尝试点击评论按钮
                    comment_btn = page.locator('button:has-text("评论"), .comment-btn').first
                    if comment_btn.is_visible():
                        comment_btn.click()
                        self.random_delay(1000, 2000)
                        comment_input = page.locator('textarea[placeholder*="评论"], input[placeholder*="评论"], .comment-input').first
                
                if comment_input.is_visible():
                    # 生成评论内容
                    comment_text = self.generate_comment_with_gpt(note_content)
                    
                    # 输入评论
                    self.human_like_typing(page, comment_input, comment_text)
                    self.random_delay(1000, 2000)
                    
                    # 点击发送按钮
                    send_btn = page.locator('button:has-text("发送"), button:has-text("评论"), .send-btn').first
                    if send_btn.is_visible():
                        send_btn.click()
                        self.random_delay(2000, 4000)
                        
                        # 检查评论是否发送成功
                        try:
                            # 查找刚发送的评论
                            new_comment = page.locator(f'text="{comment_text}"').first
                            if new_comment.is_visible():
                                self.logger.info(f"评论发送成功: {comment_text}")
                                return True
                            else:
                                self.logger.warning("评论可能已发送，但未找到确认元素")
                                return True
                        except:
                            self.logger.warning("评论发送状态检查超时，可能已成功")
                            return True
                    else:
                        self.logger.error("未找到发送按钮")
                        return False
                else:
                    self.logger.error("未找到评论输入框")
                    return False
                    
            except Exception as e:
                self.logger.error(f"评论笔记时出现错误: {e}")
                return False
            finally:
                browser.close()
    
    def reply_to_multiple_notes(self, note_urls: list, max_comments: int = None) -> dict:
        """对多个笔记进行评论回复"""
        if max_comments is None:
            max_comments = self.config['commenting']['max_comments_per_day']
        
        if not note_urls:
            self.logger.warning("没有提供笔记链接")
            return {}
        
        results = {}
        comments_count = 0
        
        for account in self.config['accounts']:
            if comments_count >= max_comments:
                break
                
            account_name = account['name']
            
            # 验证登录状态
            if not self.login_manager.verify_login_status(account_name):
                self.logger.warning(f"账号 {account_name} 登录状态无效，跳过")
                continue
            
            # 为每个账号评论笔记
            for note_url in note_urls:
                if comments_count >= max_comments:
                    break
                
                success = self.reply_to_note(account_name, note_url)
                results[f"{account_name}_{note_url}"] = success
                
                if success:
                    comments_count += 1
                
                # 评论间隔
                if len(note_urls) > 1:
                    interval_minutes = self.config['commenting']['min_interval_minutes']
                    if interval_minutes:
                        self.logger.info(f"等待 {interval_minutes} 分钟后继续评论...")
                        time.sleep(interval_minutes * 60)
        
        return results
    
    def reply_to_target_notes(self) -> dict:
        """对配置中的目标笔记进行评论"""
        target_notes = self.config['commenting']['target_notes']
        return self.reply_to_multiple_notes(target_notes)
    
    def create_sample_target_notes(self):
        """创建示例目标笔记配置"""
        sample_notes = [
            "https://www.xiaohongshu.com/explore/示例笔记ID1",
            "https://www.xiaohongshu.com/explore/示例笔记ID2"
        ]
        
        # 更新配置文件
        self.config['commenting']['target_notes'] = sample_notes
        
        with open("config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info("已更新配置文件，添加了示例目标笔记")

if __name__ == "__main__":
    # 测试评论功能
    gpt_reply = GPTReply()
    
    # 创建示例目标笔记
    gpt_reply.create_sample_target_notes()
    
    # 对目标笔记进行评论
    results = gpt_reply.reply_to_target_notes()
    
    print("评论结果:")
    for key, success in results.items():
        print(f"{key}: {'成功' if success else '失败'}") 