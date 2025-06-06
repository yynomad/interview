# 端口冲突解决方案

## 🔍 问题描述

"Address already in use" 错误通常是因为端口被其他进程占用。在面试助手系统中，常见的端口冲突包括：

- **端口 5000**: 被 macOS 控制中心占用
- **端口 5001**: 被其他 Flask 应用占用

## 🛠️ 解决方案

### 1. 自动修复（推荐）

运行自动修复脚本：
```bash
./fix-port-conflicts.sh
```

这个脚本会：
- 检查端口占用情况
- 自动更新配置文件
- 提供详细的解决建议

### 2. 手动检查端口

#### macOS/Linux
```bash
# 检查特定端口占用
lsof -i :5001

# 查看所有监听端口
netstat -tulpn | grep LISTEN

# 终止占用端口的进程
sudo lsof -ti :5001 | xargs kill -9
```

#### Windows
```bash
# 检查端口占用
netstat -ano | findstr :5001

# 终止进程
taskkill /F /PID <PID>
```

### 3. 使用不同端口

#### 临时解决方案
```bash
# 后端使用不同端口
PORT=5002 python backend/app.py
```

#### 永久解决方案
编辑配置文件：

**backend/.env**
```env
PORT=5001  # 或其他可用端口
```

**desktop-tool/.env**
```env
BACKEND_URL=http://localhost:5001
```

## 🔧 系统配置

### 当前端口配置

| 服务 | 端口 | 配置文件 |
|------|------|----------|
| 后端 Flask | 5001 | `backend/.env` |
| WebSocket | 5001 | 与后端相同 |

### macOS 特殊情况

在 macOS 上，端口 5000 被控制中心占用是正常现象：
```bash
# 查看控制中心进程
lsof -i :5000
# 输出: ControlCenter 1258 user ...
```

**不要终止控制中心进程**，而是使用其他端口。

## 🚀 快速修复步骤

1. **运行端口检查**：
   ```bash
   python check-ports.py
   ```

2. **自动修复配置**：
   ```bash
   ./fix-port-conflicts.sh
   ```

3. **验证配置**：
   ```bash
   grep "PORT=" backend/.env
   grep "BACKEND_URL=" desktop-tool/.env
   ```

4. **启动系统**：
   ```bash
   ./start-all.sh
   ```

## 🔍 故障排除

### 问题：后端启动失败
```
Error: [Errno 48] Address already in use
```

**解决方案**：
1. 检查端口占用：`lsof -i :5001`
2. 终止冲突进程或使用其他端口
3. 更新配置文件



### 问题：电脑端工具连接失败
```
无法连接到后端服务器
```

**解决方案**：
1. 检查 `desktop-tool/.env` 中的 `BACKEND_URL`
2. 确认后端服务正在运行
3. 测试网络连接：`ping localhost`

## 📋 预防措施

### 1. 使用非标准端口
避免使用常见端口（如 5000, 8000, 8080）：
```env
# 推荐端口配置
PORT=5001  # 后端
```

### 2. 环境隔离
为不同环境使用不同端口：
```env
# 开发环境
PORT=5001

# 测试环境
PORT=5002

# 生产环境
PORT=80 或 443
```

### 3. 进程管理
使用进程管理工具：
```bash
# 使用 supervisor 管理 Python 应用
pip install supervisor
```

## 🔗 相关工具

### 端口扫描工具
```bash
# 查找可用端口
for port in {5001..5010}; do
    ! nc -z localhost $port && echo "端口 $port 可用"
done

# 使用 nmap 扫描
nmap -p 5000-5010 localhost
```

### 进程监控
```bash
# 实时监控端口
watch "lsof -i :5001"

# 监控系统资源
htop
```

## 📞 获取帮助

如果问题仍然存在：

1. **查看日志**：检查应用日志文件
2. **运行诊断**：`python test-system.py`
3. **重启系统**：最后的解决方案
4. **联系支持**：提供错误日志和系统信息

## 📝 更新记录

- **2024-01-XX**: 初始版本
- **2024-01-XX**: 添加 macOS 控制中心解决方案
- **2024-01-XX**: 添加自动修复脚本
