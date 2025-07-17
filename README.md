# 小红书自动运营系统

一个基于 Python + Playwright + OpenAI API 的小红书自动运营工具，支持多账号管理、自动发帖、自动评论回复等功能。

## 功能特性

- 🔐 **多账号管理**: 支持多个小红书账号的Cookie隔离管理
- 📝 **自动发帖**: 从本地文案文件自动发布小红书笔记
- 🖼️ **图片上传**: 支持自动上传配图到笔记
- 💬 **智能评论**: 使用GPT API生成自然、友好的评论回复
- 🤖 **浏览器自动化**: 使用Playwright模拟真实人工操作
- ⏱️ **智能延迟**: 内置随机延迟机制，避免触发风控
- 📊 **详细日志**: 完整的操作日志记录

## 系统要求

- Python 3.8+
- Windows/macOS/Linux
- 稳定的网络连接

## 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Wechat-ai-agent
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装Playwright浏览器**
```bash
playwright install chromium
```

4. **初始化项目**
```bash
python main.py --mode setup
```

## 配置说明

### 1. 编辑配置文件

编辑 `config.yaml` 文件，配置你的账号信息：

```yaml
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
```

### 2. 准备文案和图片

- **文案文件**: 将文案保存为 `.txt` 文件放在 `drafts/` 目录
- **图片文件**: 将配图放在 `assets/` 目录，文件名与文案文件名对应

示例：
```
drafts/
  ├── 文案1.txt
  ├── 文案2.txt
  └── sample_draft.txt

assets/
  ├── 文案1_1.jpg
  ├── 文案1_2.png
  ├── 文案2_1.jpg
  └── sample_draft_1.jpg
```

## 使用方法

### 1. 完整运行（推荐）

```bash
python main.py --mode full
```

### 2. 分步运行

**扫码登录所有账号:**
```bash
python main.py --mode login
```

**扫码登录指定账号:**
```bash
python main.py --mode qr-login --account "账号1"
```

**仅发布笔记:**
```bash
python main.py --mode publish --max-posts 3
```

**仅评论回复:**
```bash
python main.py --mode comment --note-urls "https://www.xiaohongshu.com/explore/xxx" "https://www.xiaohongshu.com/explore/yyy"
```

### 3. 自定义配置

```bash
python main.py --config my_config.yaml --mode full
```

## 目录结构

```
Wechat-ai-agent/
├── main.py                 # 主程序
├── login_manager.py        # 登录管理器
├── publisher.py           # 发帖管理器
├── gpt_reply.py          # GPT回复管理器
├── config.yaml           # 配置文件
├── requirements.txt      # 依赖包
├── README.md            # 说明文档
├── drafts/              # 文案目录
│   ├── sample_draft.txt
│   └── ...
├── assets/              # 图片目录
│   ├── sample_draft_1.jpg
│   └── ...
├── cookies/             # Cookie存储目录
│   ├── account1_cookies.json
│   └── ...
└── logs/               # 日志目录
    ├── login.log
    ├── publisher.log
    ├── gpt_reply.log
    └── bot_YYYYMMDD.log
```

## 配置参数说明

### 浏览器配置
- `headless`: 是否无头模式运行（建议开发时设为false）
- `slow_mo`: 操作间隔时间（毫秒）
- `timeout`: 页面加载超时时间

### 延迟配置
- `page_load`: 页面加载后等待时间
- `element_click`: 点击元素后等待时间
- `text_input`: 文本输入间隔时间
- `upload_file`: 文件上传后等待时间
- `comment_reply`: 评论回复后等待时间

### 发帖配置
- `max_posts_per_day`: 每日最大发帖数
- `min_interval_hours`: 发帖最小间隔（小时）
- `auto_save_draft`: 是否自动保存草稿

### 评论配置
- `max_comments_per_day`: 每日最大评论数
- `min_interval_minutes`: 评论最小间隔（分钟）
- `target_notes`: 目标笔记链接列表
- `comment_templates`: 评论模板

## 登录说明

### 扫码登录流程
1. 运行登录命令后，系统会自动打开浏览器
2. 浏览器会显示小红书登录页面的二维码
3. 使用小红书APP扫描二维码进行登录
4. 登录成功后，系统会自动保存Cookie
5. 后续运行时会自动使用保存的Cookie，无需重复登录

### 登录状态管理
- Cookie会自动保存在 `cookies/` 目录
- 系统会定期验证登录状态
- 如果登录状态失效，需要重新扫码登录

## 注意事项

1. **账号安全**: 
   - 请使用真实的小红书账号
   - 建议使用小号进行测试
   - 不要频繁操作，避免账号被封

2. **操作频率**:
   - 系统已内置随机延迟，模拟人工操作
   - 可根据需要调整配置文件中的延迟参数
   - 建议每日发帖不超过5篇，评论不超过20条

3. **内容质量**:
   - 文案内容需要原创，避免抄袭
   - 图片需要版权合规
   - 评论内容要自然友好

4. **技术限制**:
   - 系统基于浏览器自动化，可能受网页结构变化影响
   - 建议定期检查更新，适应小红书界面变化

## 故障排除

### 常见问题

1. **登录失败**
   - 检查账号密码是否正确
   - 确认网络连接正常
   - 尝试手动登录验证账号状态

2. **发布失败**
   - 检查文案文件格式是否正确
   - 确认图片文件存在且格式支持
   - 查看日志文件获取详细错误信息

3. **评论失败**
   - 检查OpenAI API密钥是否正确
   - 确认目标笔记链接有效
   - 验证账号登录状态

### 日志查看

系统会生成详细的日志文件：
- `logs/login.log`: 登录相关日志
- `logs/publisher.log`: 发帖相关日志
- `logs/gpt_reply.log`: 评论相关日志
- `logs/bot_YYYYMMDD.log`: 主程序日志

## 免责声明

本工具仅供学习和研究使用，请遵守小红书平台的使用条款和相关法律法规。使用者需自行承担使用风险，开发者不承担任何法律责任。

## 更新日志

- v1.0.0: 初始版本，支持基本的多账号管理、自动发帖、自动评论功能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License
