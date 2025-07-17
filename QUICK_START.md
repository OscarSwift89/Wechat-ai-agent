# 小红书自动运营系统 - 快速开始指南

## 🚀 5分钟快速上手

### 1. 一键安装
```bash
python install.py
```

### 2. 配置账号
编辑 `config.yaml` 文件，填入你的账号信息：
```yaml
accounts:
  - name: "我的账号"
    cookie_file: "cookies/my_account_cookies.json"

openai:
  api_key: "你的OpenAI API密钥"
```

**注意：** 系统使用扫码登录，无需输入账号密码。首次运行时会打开浏览器显示二维码，使用小红书APP扫码即可登录。

### 3. 准备内容
- 在 `drafts/` 目录放入文案文件（.txt格式）
- 在 `assets/` 目录放入对应图片文件

### 4. 开始运行
```bash
python run.py
```

**首次使用需要扫码登录：**
1. 系统会自动打开浏览器显示二维码
2. 使用小红书APP扫描二维码登录
3. 登录成功后Cookie会自动保存
4. 后续运行无需重复登录

## 📁 文件结构说明

```
drafts/          # 文案目录
├── 文案1.txt    # 你的文案文件
└── 文案2.txt

assets/          # 图片目录  
├── 文案1_1.jpg  # 对应文案的图片
├── 文案1_2.png
└── 文案2_1.jpg

cookies/         # Cookie存储（自动创建）
└── *.json

logs/            # 日志文件（自动创建）
└── *.log
```

## ⚡ 常用命令

### 完整运行（推荐）
```bash
python main.py --mode full
```

### 扫码登录所有账号
```bash
python main.py --mode login
```

### 扫码登录指定账号
```bash
python main.py --mode qr-login --account "账号1"
```

### 仅发布笔记
```bash
python main.py --mode publish --max-posts 3
```

### 仅评论回复
```bash
python main.py --mode comment --note-urls "https://www.xiaohongshu.com/explore/xxx"
```

## 🔧 配置说明

### 重要配置项
- `headless: false` - 设为true可后台运行
- `slow_mo: 1000` - 操作间隔时间（毫秒）
- `max_posts_per_day: 5` - 每日最大发帖数
- `max_comments_per_day: 20` - 每日最大评论数

### 安全建议
- 建议使用小号测试
- 不要频繁操作，避免账号被封
- 文案内容需要原创
- 图片需要版权合规

## 🆘 常见问题

### Q: 扫码登录失败怎么办？
A: 
- 确保网络连接正常
- 检查小红书APP是否正常
- 重新运行登录命令
- 如果二维码不显示，请检查浏览器是否正常打开

### Q: 发布失败怎么办？
A: 检查文案文件格式，确认图片文件存在

### Q: 评论失败怎么办？
A: 检查OpenAI API密钥是否正确

### Q: 如何查看运行日志？
A: 查看 `logs/` 目录下的日志文件

## 📞 获取帮助

- 📖 详细文档：查看 `README.md`
- 🐛 问题反馈：提交Issue
- 💡 功能建议：欢迎贡献代码

## ⚠️ 免责声明

本工具仅供学习和研究使用，请遵守小红书平台的使用条款和相关法律法规。 