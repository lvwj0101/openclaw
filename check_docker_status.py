#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Docker状态和日志"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("检查Docker状态")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Docker服务...")
    output = run(ssh, 'sudo systemctl status docker --no-pager')
    print(output)

    print()
    print("[2] 检查所有Docker容器...")
    output = run(ssh, 'sudo docker ps -a')
    print(output)

    print()
    print("[3] 检查Docker Compose日志...")
    output = run(ssh, 'cd /home/ubuntu && sudo docker-compose logs', timeout=30)
    print(output)

    print()
    print("[4] 检查Docker日志...")
    output = run(ssh, 'sudo journalctl -u docker --since "10 minutes ago" --no-pager | tail -50')
    print(output)

    print()
    print("[5] 检查docker-compose文件...")
    output = run(ssh, 'cat /home/ubuntu/docker-compose.yml')
    print(output)

    print()
    print("[6] 检查.env文件...")
    output = run(ssh, 'cat /home/ubuntu/mailu.env')
    print(output)

    print()
    print("[7] 尝试启动Docker...")
    output = run(ssh, 'cd /home/ubuntu && sudo docker-compose up -d --force-recreate', timeout=60)
    print(output)

    print()
    print("[8] 检查容器...")
    output = run(ssh, 'sudo docker ps -a')
    print(output)

    print()
    print("="*60)
    print("Docker状态检查完成")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 检查失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
