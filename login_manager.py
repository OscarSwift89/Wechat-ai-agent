import json
import os
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
import yaml
import logging

class LoginManager:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化登录管理器"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.cookies_dir = Path(self.config['paths']['cookies'])
        self.cookies_dir.mkdir(exist_ok=True)
        
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
                logging.FileHandler(log_dir / 'login.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_cookies(self, account_name: str) -> dict:
        """加载指定账号的Cookie"""
        cookie_file = self.cookies_dir / f"{account_name}_cookies.json"
        if cookie_file.exists():
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                self.logger.info(f"成功加载账号 {account_name} 的Cookie")
                return cookies
            except Exception as e:
                self.logger.error(f"加载Cookie失败: {e}")
        return {}
    
    def save_cookies(self, account_name: str, cookies: list):
        """保存指定账号的Cookie"""
        cookie_file = self.cookies_dir / f"{account_name}_cookies.json"
        try:
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功保存账号 {account_name} 的Cookie")
        except Exception as e:
            self.logger.error(f"保存Cookie失败: {e}")
    
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
    
    def login_account(self, account: dict) -> bool:
        """登录指定账号（扫码登录）"""
        account_name = account['name']
        
        self.logger.info(f"开始扫码登录账号: {account_name}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # 扫码登录需要显示浏览器
                slow_mo=self.config['browser']['slow_mo']
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            page.set_default_timeout(self.config['browser']['timeout'])
            
            try:
                # 访问小红书登录页面
                page.goto("https://www.xiaohongshu.com/login")
                self.random_delay(2000, 4000)
                
                # 等待页面加载
                page.wait_for_load_state("networkidle")
                
                # 查找并点击扫码登录按钮（如果存在）
                try:
                    qr_login_btn = page.locator("text=扫码登录, text=二维码登录, .qr-login-btn").first
                    if qr_login_btn.is_visible():
                        qr_login_btn.click()
                        self.random_delay(1000, 2000)
                except:
                    pass
                
                # 等待二维码出现
                qr_code = page.locator('.qr-code, .qrcode, [data-testid="qr-code"]').first
                if qr_code.is_visible():
                    self.logger.info(f"请使用小红书APP扫描二维码登录账号: {account_name}")
                    print(f"\n📱 请使用小红书APP扫描二维码登录账号: {account_name}")
                    print("⏳ 等待扫码登录...")
                    
                    # 等待用户扫码登录
                    # 检测登录成功：URL变化或出现用户头像
                    max_wait_time = 120  # 最多等待2分钟
                    start_time = time.time()
                    
                    while time.time() - start_time < max_wait_time:
                        try:
                            # 检查是否已登录（URL变化或出现用户头像）
                            current_url = page.url
                            if "login" not in current_url.lower():
                                # 进一步检查是否真的登录成功
                                user_avatar = page.locator('[data-testid="user-avatar"], .avatar, .user-avatar').first
                                if user_avatar.is_visible():
                                    # 保存Cookie
                                    cookies = context.cookies()
                                    self.save_cookies(account_name, cookies)
                                    
                                    self.logger.info(f"账号 {account_name} 扫码登录成功")
                                    print(f"✅ 账号 {account_name} 登录成功！")
                                    return True
                            
                            # 检查是否还在登录页面
                            if "login" in current_url.lower():
                                time.sleep(2)  # 继续等待
                                continue
                            else:
                                # URL已变化，可能登录成功
                                time.sleep(3)  # 等待页面完全加载
                                user_avatar = page.locator('[data-testid="user-avatar"], .avatar, .user-avatar').first
                                if user_avatar.is_visible():
                                    # 保存Cookie
                                    cookies = context.cookies()
                                    self.save_cookies(account_name, cookies)
                                    
                                    self.logger.info(f"账号 {account_name} 扫码登录成功")
                                    print(f"✅ 账号 {account_name} 登录成功！")
                                    return True
                                else:
                                    # URL变化但未检测到登录成功，继续等待
                                    time.sleep(2)
                                    continue
                                    
                        except Exception as e:
                            self.logger.debug(f"等待登录时出现异常: {e}")
                            time.sleep(2)
                            continue
                    
                    # 超时
                    self.logger.error(f"账号 {account_name} 扫码登录超时")
                    print(f"❌ 账号 {account_name} 登录超时，请重试")
                    return False
                else:
                    self.logger.error(f"未找到二维码，可能页面结构已变化")
                    print(f"❌ 未找到二维码，请检查页面")
                    return False
                    
            except Exception as e:
                self.logger.error(f"扫码登录过程中出现错误: {e}")
                print(f"❌ 登录过程中出现错误: {e}")
                return False
            finally:
                # 询问用户是否关闭浏览器
                try:
                    user_input = input("\n是否关闭浏览器窗口？(y/n): ").lower().strip()
                    if user_input in ['y', 'yes', '是']:
                        browser.close()
                    else:
                        print("浏览器窗口保持打开状态，请手动关闭")
                except:
                    browser.close()
    
    def login_all_accounts(self) -> dict:
        """登录所有配置的账号"""
        results = {}
        
        for account in self.config['accounts']:
            success = self.login_account(account)
            results[account['name']] = success
            
            # 账号间登录间隔
            if len(self.config['accounts']) > 1:
                print(f"\n⏳ 等待 {self.config['delays']['page_load']/1000} 秒后登录下一个账号...")
                self.random_delay(5000, 10000)
        
        return results
    
    def login_single_account(self, account_name: str) -> bool:
        """登录单个指定账号"""
        account = None
        for acc in self.config['accounts']:
            if acc['name'] == account_name:
                account = acc
                break
        
        if not account:
            self.logger.error(f"未找到账号: {account_name}")
            return False
        
        return self.login_account(account)
    
    def verify_login_status(self, account_name: str) -> bool:
        """验证账号登录状态"""
        cookies = self.load_cookies(account_name)
        if not cookies:
            return False
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            # 添加Cookie
            context.add_cookies(cookies)
            
            page = context.new_page()
            
            try:
                page.goto("https://www.xiaohongshu.com")
                page.wait_for_load_state("networkidle")
                
                # 检查是否已登录（查找用户头像或用户名等元素）
                user_avatar = page.locator('[data-testid="user-avatar"], .avatar, .user-avatar').first
                if user_avatar.is_visible():
                    self.logger.info(f"账号 {account_name} 登录状态有效")
                    return True
                else:
                    self.logger.warning(f"账号 {account_name} 登录状态已失效")
                    return False
                    
            except Exception as e:
                self.logger.error(f"验证登录状态时出错: {e}")
                return False
            finally:
                browser.close()

if __name__ == "__main__":
    # 测试登录功能
    login_manager = LoginManager()
    results = login_manager.login_all_accounts()
    
    print("登录结果:")
    for account, success in results.items():
        print(f"{account}: {'成功' if success else '失败'}") 