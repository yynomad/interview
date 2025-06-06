# Git 忽略文件说明

本文档说明了面试助手系统中 `.gitignore` 文件的配置规则和原因。

## 🔐 敏感信息保护

### 环境配置文件
```
.env
.env.local
backend/.env
desktop-tool/.env
```

**原因**: 这些文件包含 API 密钥、数据库密码等敏感信息，绝对不能提交到版本控制系统。

**注意**: 
- 提供 `.env.example` 文件作为模板
- 团队成员需要根据模板创建自己的 `.env` 文件

### API 密钥和凭证
```
*.key
*.pem
credentials.json
```

**原因**: 防止意外提交私钥、证书等敏感文件。

## 🐍 Python 项目文件

### 编译文件
```
__pycache__/
*.py[cod]
*.so
```

**原因**: Python 字节码文件是自动生成的，不需要版本控制。

### 虚拟环境
```
.venv/
venv/
env/
```

**原因**: 虚拟环境包含大量文件，应该通过 `requirements.txt` 管理依赖。

### 包分发文件
```
build/
dist/
*.egg-info/
```

**原因**: 这些是构建过程中生成的文件，不需要版本控制。





## 🎤 音频文件

### 临时录音
```
temp_audio_*.wav
*.tmp.wav
recordings/
```

**原因**: 
- 临时音频文件体积大
- 可能包含隐私信息
- 不是项目核心代码

### Whisper 模型缓存
```
.cache/whisper/
```

**原因**: Whisper 模型文件很大，会自动下载，不需要版本控制。

## 📝 日志和数据文件

### 日志文件
```
*.log
logs/
```

**原因**: 日志文件包含运行时信息，不是源代码的一部分。

### 数据库文件
```
*.db
*.sqlite
conversation_history.json
```

**原因**: 
- 数据库文件包含用户数据
- 可能包含隐私信息
- 应该通过数据库迁移管理结构

## 💻 开发工具文件

### IDE 配置
```
.vscode/
.idea/
*.sublime-workspace
```

**原因**: IDE 配置是个人偏好，不应该强制给团队其他成员。

**例外**: 可以提交一些通用的 VSCode 设置，如 `.vscode/settings.json`。

### 操作系统文件
```
.DS_Store
Thumbs.db
```

**原因**: 操作系统自动生成的文件，对项目无用。

## 🚀 部署和云服务

### Docker 本地文件
```
Dockerfile.local
```

**原因**: 本地开发用的 Docker 配置可能包含敏感信息。

### Terraform 状态
```
*.tfstate
.terraform/
```

**原因**: Terraform 状态文件可能包含敏感信息，应该存储在远程后端。

## 📋 最佳实践

### 1. 定期检查
```bash
# 检查是否有敏感文件被意外添加
git status
git diff --cached
```

### 2. 全局 gitignore
为常见的系统文件设置全局忽略：
```bash
git config --global core.excludesfile ~/.gitignore_global
```

### 3. 已提交文件的处理
如果敏感文件已经被提交：
```bash
# 从版本控制中移除但保留本地文件
git rm --cached .env

# 添加到 .gitignore
echo ".env" >> .gitignore

# 提交更改
git add .gitignore
git commit -m "Remove .env from version control"
```

### 4. 团队协作
- 确保所有团队成员了解 `.gitignore` 规则
- 定期更新 `.gitignore` 文件
- 在 README 中说明环境配置步骤

## ⚠️ 注意事项

1. **不要忽略示例文件**: `.env.example` 应该被提交，作为配置模板。

2. **检查大文件**: 使用 `git ls-files --others --ignored --exclude-standard` 查看被忽略的文件。

3. **敏感信息泄露**: 如果意外提交了敏感信息，需要：
   - 立即更改相关密钥
   - 使用 `git filter-branch` 或 BFG Repo-Cleaner 清理历史
   - 通知团队成员

4. **定期清理**: 定期清理临时文件和缓存：
   ```bash
   # 清理 Python 缓存
   find . -type d -name "__pycache__" -delete
   
   # 清理临时音频文件
   rm -f temp_audio_*.wav
   ```

## 🔍 验证 .gitignore

使用以下命令验证 `.gitignore` 是否正常工作：

```bash
# 检查特定文件是否被忽略
git check-ignore .env

# 查看所有被忽略的文件
git ls-files --others --ignored --exclude-standard

# 强制添加被忽略的文件（谨慎使用）
git add -f filename
```
