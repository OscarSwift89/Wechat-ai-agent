import json
import os
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
import yaml
import logging
from datetime import datetime, timedelta
from login_manager import LoginManager

class Publisher:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化发帖管理器"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.login_manager = LoginManager(config_path)
        
        # 创建必要的目录
        self.drafts_dir = Path(self.config['paths']['drafts'])
        self.assets_dir = Path(self.config['paths']['assets'])
        self.drafts_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
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
                logging.FileHandler(log_dir / 'publisher.log', encoding='utf-8'),
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
    
    def get_draft_files(self) -> list:
        """获取所有文案文件"""
        draft_files = []
        for file in self.drafts_dir.glob("*.txt"):
            draft_files.append(file)
        return draft_files
    
    def get_assets_for_draft(self, draft_file: Path) -> list:
        """获取对应文案的图片文件"""
        assets = []
        base_name = draft_file.stem
        
        # 查找对应的图片文件
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
            for file in self.assets_dir.glob(f"{base_name}_{ext}"):
                assets.append(file)
            # 也查找不带后缀的文件
            for file in self.assets_dir.glob(f"{base_name}{ext}"):
                assets.append(file)
        
        return assets
    
    def read_draft_content(self, draft_file: Path) -> str:
        """读取文案内容"""
        try:
            with open(draft_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"读取文案文件失败 {draft_file}: {e}")
            return ""
    
    def publish_note(self, account_name: str, draft_file: Path) -> bool:
        """发布单篇笔记"""
        self.logger.info(f"开始发布笔记: {draft_file.name} (账号: {account_name})")
        
        # 读取文案内容
        content = self.read_draft_content(draft_file)
        if not content:
            self.logger.error(f"文案内容为空: {draft_file}")
            return False
        
        # 获取对应的图片文件
        assets = self.get_assets_for_draft(draft_file)
        
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
                # 访问小红书创作页面
                page.goto("https://creator.xiaohongshu.com/publish/publish")
                self.random_delay(3000, 5000)
                
                # 等待页面加载
                page.wait_for_load_state("networkidle")
                
                # 检查是否已登录
                try:
                    # 查找登录提示或重定向到登录页面
                    if "login" in page.url.lower():
                        self.logger.error(f"账号 {account_name} 登录状态已失效")
                        return False
                except:
                    pass
                
                # 等待创作页面加载完成
                page.wait_for_selector('div[contenteditable="true"], textarea, .editor', timeout=10000)
                self.random_delay()
                
                # 输入文案内容
                editor = page.locator('div[contenteditable="true"], textarea, .editor').first
                if editor.is_visible():
                    self.human_like_typing(page, editor, content)
                    self.random_delay()
                
                # 上传图片
                if assets:
                    self.logger.info(f"准备上传 {len(assets)} 张图片")
                    
                    # 查找上传按钮
                    upload_btn = page.locator('input[type="file"], .upload-btn, [data-testid="upload"]').first
                    if upload_btn.is_visible():
                        # 上传所有图片
                        file_paths = [str(asset) for asset in assets]
                        upload_btn.set_input_files(file_paths)
                        
                        self.logger.info(f"开始上传图片: {file_paths}")
                        self.random_delay(3000, 5000)
                        
                        # 等待图片上传完成
                        try:
                            page.wait_for_selector('.upload-success, .uploaded', timeout=30000)
                            self.logger.info("图片上传完成")
                        except:
                            self.logger.warning("图片上传状态检查超时，继续执行")
                
                # 添加话题标签（可选）
                if "#" in content:
                    self.logger.info("检测到话题标签，等待话题自动识别")
                    self.random_delay(2000, 4000)
                
                # 点击发布按钮
                publish_btn = page.locator('button:has-text("发布"), button:has-text("发 布"), .publish-btn').first
                if publish_btn.is_visible():
                    self.logger.info("点击发布按钮")
                    publish_btn.click()
                    self.random_delay(3000, 5000)
                    
                    # 等待发布完成
                    try:
                        page.wait_for_selector('.publish-success, .success-message', timeout=30000)
                        self.logger.info(f"笔记发布成功: {draft_file.name}")
                        
                        # 移动已发布的文件到已发布目录
                        self._move_published_file(draft_file)
                        
                        return True
                    except:
                        self.logger.warning("发布状态检查超时，可能已发布成功")
                        return True
                else:
                    self.logger.error("未找到发布按钮")
                    return False
                    
            except Exception as e:
                self.logger.error(f"发布笔记时出现错误: {e}")
                return False
            finally:
                browser.close()
    
    def _move_published_file(self, draft_file: Path):
        """移动已发布的文件到已发布目录"""
        try:
            published_dir = self.drafts_dir / "published"
            published_dir.mkdir(exist_ok=True)
            
            # 移动文案文件
            new_path = published_dir / f"{draft_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            draft_file.rename(new_path)
            
            # 移动对应的图片文件
            assets = self.get_assets_for_draft(draft_file)
            for asset in assets:
                if asset.exists():
                    asset_new_path = published_dir / f"{asset.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{asset.suffix}"
                    asset.rename(asset_new_path)
            
            self.logger.info(f"已移动已发布文件到: {published_dir}")
        except Exception as e:
            self.logger.error(f"移动已发布文件失败: {e}")
    
    def publish_all_drafts(self, max_posts: int = None) -> dict:
        """发布所有文案"""
        if max_posts is None:
            max_posts = self.config['publishing']['max_posts_per_day']
        
        draft_files = self.get_draft_files()
        if not draft_files:
            self.logger.warning("没有找到可发布的文案文件")
            return {}
        
        results = {}
        posts_count = 0
        
        for account in self.config['accounts']:
            if posts_count >= max_posts:
                break
                
            account_name = account['name']
            
            # 验证登录状态
            if not self.login_manager.verify_login_status(account_name):
                self.logger.warning(f"账号 {account_name} 登录状态无效，跳过")
                continue
            
            # 为每个账号发布文案
            for draft_file in draft_files:
                if posts_count >= max_posts:
                    break
                
                success = self.publish_note(account_name, draft_file)
                results[f"{account_name}_{draft_file.name}"] = success
                
                if success:
                    posts_count += 1
                
                # 发帖间隔
                if len(draft_files) > 1:
                    interval_hours = self.config['publishing']['min_interval_hours']
                    if interval_hours:
                        self.logger.info(f"等待 {interval_hours} 小时后继续发布...")
                        time.sleep(interval_hours * 3600)
        
        return results
    
    def create_sample_draft(self):
        """创建示例文案文件"""
        sample_content = """# 小红书文案示例

这是一篇示例文案，你可以在这里写你的笔记内容。

## 主要内容
- 第一点
- 第二点  
- 第三点

## 总结
这是一个很好的分享，希望对大家有帮助！

#小红书 #示例 #分享"""
        
        sample_file = self.drafts_dir / "sample_draft.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        self.logger.info(f"已创建示例文案文件: {sample_file}")

if __name__ == "__main__":
    # 测试发帖功能
    publisher = Publisher()
    
    # 创建示例文案
    publisher.create_sample_draft()
    
    # 发布所有文案
    results = publisher.publish_all_drafts(max_posts=2)
    
    print("发布结果:")
    for key, success in results.items():
        print(f"{key}: {'成功' if success else '失败'}") 