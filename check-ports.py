#!/usr/bin/env python3
"""
端口检查和修复脚本
检查端口占用情况并提供解决方案
"""

import subprocess
import sys
import os
import socket
import signal
import time
from typing import List, Dict, Optional

def check_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except Exception:
        return False

def get_process_using_port(port: int) -> Optional[Dict]:
    """获取占用端口的进程信息"""
    try:
        if sys.platform == "darwin" or sys.platform.startswith("linux"):
            # macOS 和 Linux
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-t'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                
                # 获取进程详细信息
                ps_result = subprocess.run(
                    ['ps', '-p', pid, '-o', 'pid,ppid,command'],
                    capture_output=True,
                    text=True
                )
                if ps_result.returncode == 0:
                    lines = ps_result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split(None, 2)
                        return {
                            'pid': int(parts[0]),
                            'ppid': int(parts[1]),
                            'command': parts[2] if len(parts) > 2 else 'Unknown'
                        }
        
        elif sys.platform == "win32":
            # Windows
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = int(parts[-1])
                            
                            # 获取进程名称
                            tasklist_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                                capture_output=True,
                                text=True
                            )
                            if tasklist_result.returncode == 0:
                                lines = tasklist_result.stdout.strip().split('\n')
                                if len(lines) > 1:
                                    command = lines[1].split(',')[0].strip('"')
                                    return {
                                        'pid': pid,
                                        'ppid': 0,
                                        'command': command
                                    }
    except Exception as e:
        print(f"获取进程信息时出错: {e}")
    
    return None

def kill_process(pid: int) -> bool:
    """终止进程"""
    try:
        if sys.platform == "win32":
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            # 如果进程仍然存在，强制终止
            try:
                os.kill(pid, 0)  # 检查进程是否还存在
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # 进程已经不存在
        return True
    except Exception as e:
        print(f"终止进程失败: {e}")
        return False

def find_available_port(start_port: int, max_attempts: int = 100) -> Optional[int]:
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if not check_port_in_use(port):
            return port
    return None

def check_config_files() -> Dict[str, int]:
    """检查配置文件中的端口设置"""
    ports = {}
    
    # 检查后端配置
    backend_env_files = [
        'backend/.env',
        'backend/.env.development',
        'backend/.env.production'
    ]
    
    for file_path in backend_env_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.startswith('PORT='):
                            port = int(line.split('=')[1].strip())
                            ports[file_path] = port
                            break
            except Exception as e:
                print(f"读取 {file_path} 失败: {e}")
    
    # 检查前端配置
    frontend_package_json = 'frontend/package.json'
    if os.path.exists(frontend_package_json):
        try:
            import json
            with open(frontend_package_json, 'r') as f:
                data = json.load(f)
                # Next.js 默认端口是 3000
                ports[frontend_package_json] = 3000
        except Exception as e:
            print(f"读取 {frontend_package_json} 失败: {e}")
    
    return ports

def fix_port_conflicts():
    """修复端口冲突"""
    print("🔍 检查端口配置...")
    
    # 检查配置文件中的端口
    config_ports = check_config_files()
    
    # 检查常用端口
    common_ports = [3000, 5000, 5001, 8000, 8080]
    
    print("\n📋 端口使用情况:")
    print("-" * 50)
    
    conflicts = []
    
    for port in common_ports:
        in_use = check_port_in_use(port)
        status = "🔴 占用" if in_use else "🟢 可用"
        print(f"端口 {port}: {status}")
        
        if in_use:
            process_info = get_process_using_port(port)
            if process_info:
                print(f"    进程: PID {process_info['pid']} - {process_info['command']}")
                conflicts.append((port, process_info))
            else:
                print(f"    进程: 无法获取进程信息")
                conflicts.append((port, None))
    
    print("\n📁 配置文件中的端口:")
    print("-" * 50)
    for file_path, port in config_ports.items():
        in_use = check_port_in_use(port)
        status = "🔴 冲突" if in_use else "🟢 正常"
        print(f"{file_path}: {port} {status}")
    
    # 处理冲突
    if conflicts:
        print(f"\n⚠️  发现 {len(conflicts)} 个端口冲突")
        
        for port, process_info in conflicts:
            if process_info:
                print(f"\n端口 {port} 被进程占用:")
                print(f"  PID: {process_info['pid']}")
                print(f"  命令: {process_info['command']}")
                
                # 检查是否是我们自己的服务
                if any(keyword in process_info['command'].lower() 
                       for keyword in ['python', 'node', 'npm', 'flask', 'next']):
                    
                    choice = input(f"是否终止此进程？(y/n) [默认: n]: ").strip().lower()
                    if choice in ['y', 'yes', '是']:
                        if kill_process(process_info['pid']):
                            print(f"✅ 进程 {process_info['pid']} 已终止")
                        else:
                            print(f"❌ 无法终止进程 {process_info['pid']}")
                else:
                    print("⚠️  这不是我们的服务进程，建议手动处理")
    
    # 建议可用端口
    print(f"\n💡 建议的可用端口:")
    backend_port = find_available_port(5000)
    frontend_port = find_available_port(3000)
    
    if backend_port:
        print(f"  后端: {backend_port}")
    if frontend_port:
        print(f"  前端: {frontend_port}")
    
    # 提供修复建议
    print(f"\n🔧 修复建议:")
    print("1. 终止冲突的进程（如果是旧的服务实例）")
    print("2. 修改配置文件中的端口号")
    print("3. 使用环境变量覆盖端口设置")
    print("4. 重启系统（最后手段）")

def show_port_commands():
    """显示端口相关的常用命令"""
    print("\n📚 常用端口管理命令:")
    print("-" * 50)
    
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        print("# 查看端口占用")
        print("lsof -i :5000")
        print("netstat -tulpn | grep :5000")
        print("")
        print("# 终止进程")
        print("kill -9 <PID>")
        print("pkill -f 'python.*app.py'")
        print("")
        print("# 查找可用端口")
        print("for port in {5000..5010}; do ! nc -z localhost $port && echo $port; done")
    
    elif sys.platform == "win32":
        print("# 查看端口占用")
        print("netstat -ano | findstr :5000")
        print("")
        print("# 终止进程")
        print("taskkill /F /PID <PID>")
        print("taskkill /F /IM python.exe")
        print("")
    
    print("\n# 环境变量方式启动")
    print("PORT=5001 python backend/app.py")
    print("PORT=3001 npm run dev")

def main():
    """主函数"""
    print("🔧 面试助手系统 - 端口检查工具")
    print("=" * 50)
    
    try:
        fix_port_conflicts()
        show_port_commands()
        
        print(f"\n✅ 端口检查完成")
        print("如果问题仍然存在，请手动检查并终止相关进程")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 检查过程中出现错误: {e}")

if __name__ == "__main__":
    main()
