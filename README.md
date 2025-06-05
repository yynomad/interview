# 🎤 面试助手系统

一个实时语音转文本的智能面试助手系统，帮助你在面试中获得 AI 回答建议。

## 🏗️ 系统架构

### 1. 电脑端工具 (Python)
- 🎙️ 实时监听麦克风音频
- 🔄 使用 Whisper 将音频转为文本
- ⌨️ 快捷键控制 AI 回答
- 📤 自动上传文本到后端

### 2. 后端服务器 (Flask)
- 📥 接收问题文本
- 🤖 调用 Gemini API 生成回答
- 🔌 WebSocket 推送到前端

### 3. Web 前端 (Next.js)
- 💬 实时显示问答对话
- 🎨 美观的聊天界面
- 📜 自动滚动到最新消息

## 🚀 快速开始

### 方法一：一键启动（推荐）
```bash
# 1. 初始化项目（首次使用）
./init-project.sh

# 2. 安装语音识别 SDK
python install-speech-providers.py

# 3. 运行配置向导
python setup-config.py

# 4. 启动所有服务
./start-all.sh
```

### 方法二：手动启动

#### 1. 配置环境

##### 方法一：使用环境切换脚本（推荐）
```bash
# 切换到开发环境
./switch-env.sh development

# 或切换到生产环境
./switch-env.sh production
```

##### 方法二：手动配置
```bash
# 复制配置文件并填写 API 密钥
cp backend/.env.development backend/.env
cp desktop-tool/.env.development desktop-tool/.env

# 编辑配置文件，填写 Gemini API 密钥
# backend/.env: 设置 GEMINI_API_KEY
# desktop-tool/.env: 可选设置 OPENAI_API_KEY（如果使用 OpenAI Whisper API）
```

#### 2. 启动后端服务器
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

#### 4. 运行电脑端工具
```bash
cd desktop-tool
pip install -r requirements.txt
python main.py
```

## 🧪 系统测试
```bash
# 测试系统是否正常工作
python test-system.py
```

## ⌨️ 使用说明

### 快捷键
- `Cmd+Shift+N` (macOS) / `Ctrl+Shift+N` (Windows): 切换 AI 回答模式

### 工作流程
1. 🎤 启动电脑端工具，开始监听麦克风
2. 🗣️ 面试官说话时，系统自动识别并上传文本
3. ⌨️ 按快捷键启用 AI 模式，系统会生成回答建议
4. 💻 在 Web 界面查看实时对话和 AI 建议

## 🔧 环境配置说明

### 🔄 环境切换
```bash
# 切换到开发环境
./switch-env.sh development

# 切换到生产环境
./switch-env.sh production
```

### 环境类型

#### 🛠️ 开发环境 (development)
- **DEBUG**: 启用调试模式
- **日志级别**: DEBUG（详细日志）
- **音频文件**: 保存到本地用于调试
- **Whisper**: 使用本地模型
- **CORS**: 允许本地域名访问

#### 🚀 生产环境 (production)
- **DEBUG**: 禁用调试模式
- **日志级别**: WARNING（仅重要信息）
- **音频文件**: 不保存到本地
- **Whisper**: 可使用 OpenAI API
- **CORS**: 限制特定域名访问
- **安全**: 启用速率限制

### 配置文件说明

#### 后端配置文件
```bash
backend/.env.development    # 开发环境配置
backend/.env.production     # 生产环境配置
backend/.env               # 当前使用的配置（由脚本生成）
```

#### 电脑端工具配置文件
```bash
desktop-tool/.env.development    # 开发环境配置
desktop-tool/.env.production     # 生产环境配置
desktop-tool/.env               # 当前使用的配置（由脚本生成）
```

### 关键配置项

#### 后端 (backend/.env)
```env
# 必填项
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_super_secure_secret_key

# 环境相关
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG

# 服务器配置
HOST=0.0.0.0
PORT=5001
CORS_ORIGINS=http://localhost:3000
```

#### 电脑端工具 (desktop-tool/.env)
```env
# 服务器连接
BACKEND_URL=http://localhost:5001

# 语音识别配置
SPEECH_PROVIDER=local_whisper
SPEECH_LANGUAGE=zh-CN

# 本地 Whisper 配置
WHISPER_MODEL=base

# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here

# 腾讯云配置
TENCENT_SECRET_ID=your_tencent_secret_id_here
TENCENT_SECRET_KEY=your_tencent_secret_key_here
TENCENT_REGION=ap-beijing

# 录音参数
SILENCE_THRESHOLD=0.01
SILENCE_DURATION=2.0
MIN_RECORDING_DURATION=1.0

# 调试选项
DEBUG=True
SAVE_AUDIO_FILES=True
```

## 🎤 语音识别提供商

### 支持的提供商

#### 1. 🆓 本地 Whisper (推荐新手)
- **优点**: 免费、隐私保护、离线可用
- **缺点**: 需要本地计算资源、首次下载模型
- **配置**: `SPEECH_PROVIDER=local_whisper`

#### 2. 🌟 OpenAI Whisper API
- **优点**: 高质量、快速响应
- **缺点**: 付费使用
- **配置**: `SPEECH_PROVIDER=openai`
- **获取密钥**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### 3. 🇨🇳 腾讯云语音识别 (推荐中文)
- **优点**: 中文优化、价格合理、稳定可靠
- **缺点**: 付费使用
- **配置**: `SPEECH_PROVIDER=tencent`
- **获取密钥**: [腾讯云控制台](https://console.cloud.tencent.com/cam/capi)

#### 4. 🇨🇳 阿里云语音识别
- **优点**: 中文优化、企业级服务
- **缺点**: 付费使用
- **配置**: `SPEECH_PROVIDER=aliyun`
- **获取密钥**: [阿里云控制台](https://ram.console.aliyun.com/manage/ak)

#### 5. 🇨🇳 百度云语音识别
- **优点**: 中文优化、丰富的语音能力
- **缺点**: 付费使用
- **配置**: `SPEECH_PROVIDER=baidu`
- **获取密钥**: [百度云控制台](https://console.bce.baidu.com/iam/#/iam/accesslist)

### 提供商选择建议

#### 🎯 使用场景推荐
- **个人学习/测试**: 本地 Whisper
- **中文面试场景**: 腾讯云 > 阿里云 > 百度云
- **英文面试场景**: OpenAI > 本地 Whisper
- **企业部署**: 腾讯云/阿里云（根据现有云服务选择）

#### 💰 成本考虑
- **免费**: 本地 Whisper
- **低成本**: 腾讯云、百度云
- **高质量**: OpenAI、阿里云

## 📋 系统要求

### 软件要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 硬件要求
- 麦克风设备
- 网络连接（用于 API 调用）
- 至少 4GB RAM（用于本地 Whisper 模型）

## 🔍 故障排除

### 常见问题

#### 1. 麦克风无法访问
```bash
# macOS: 检查系统偏好设置 > 安全性与隐私 > 麦克风
# Windows: 检查设置 > 隐私 > 麦克风
```

#### 2. Whisper 模型下载失败
```bash
# 手动下载模型
python -c "import whisper; whisper.load_model('base')"
```

#### 3. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 4. 端口被占用
```bash
# 自动修复端口冲突
./fix-port-conflicts.sh

# 手动检查端口占用
lsof -i :5001  # 后端端口
lsof -i :3000  # 前端端口

# 修改配置文件中的端口号
```

**详细解决方案**: 参见 [PORT_CONFLICT_SOLUTION.md](PORT_CONFLICT_SOLUTION.md)

#### 5. Git 和版本控制问题
```bash
# 意外提交了 .env 文件
git rm --cached .env
git commit -m "Remove .env from version control"

# 检查被忽略的文件
git check-ignore .env

# 查看所有被忽略的文件
git ls-files --others --ignored --exclude-standard
```

#### 6. 权限问题
```bash
# macOS/Linux 脚本权限
chmod +x init-project.sh
chmod +x start-all.sh
chmod +x switch-env.sh

# 麦克风权限
# macOS: 系统偏好设置 > 安全性与隐私 > 麦克风
# Windows: 设置 > 隐私 > 麦克风
```

## 🔗 相关链接

- [Gemini API 文档](https://ai.google.dev/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Next.js 文档](https://nextjs.org/docs)
- [Flask-SocketIO 文档](https://flask-socketio.readthedocs.io/)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本系统仅供学习和研究使用，请遵守相关法律法规和面试规则。
