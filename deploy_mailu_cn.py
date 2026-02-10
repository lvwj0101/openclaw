#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用国内镜像源重新部署Mailu"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '49.233.89.28',
    'port': 22,
    'username': 'ubuntu',
    'password': 'dyc#10010'
}

# 使用阿里云镜像
MAILU_IMAGE = 'registry.cn-hangzhou.aliyuncs.com/mailserver/mailu'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("使用国内镜像源 - Mailu部署")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 清理旧容器...")
    run(ssh, 'sudo docker stop mailu_server 2>/dev/null || true')
    run(ssh, 'sudo docker rm mailu_server 2>/dev/null || true')
    run(ssh, 'sudo docker stop mailu 2>/dev/null || true')
    run(ssh, 'sudo docker rm mailu 2>/dev/null || true')
    print("[OK] 旧容器已清理")
    print()

    print("[2] 配置Docker镜像源...")
    # 配置Docker使用阿里云镜像加速
    daemon_json = '''{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}'''
    run(ssh, f'echo \'{daemon_json}\' | sudo tee /etc/docker/daemon.json')
    run(ssh, 'sudo systemctl restart docker')
    time.sleep(5)
    print("[OK] Docker镜像源已配置")
    print()

    print("[3] 拉取Mailu镜像...")
    output = run(ssh, f'sudo docker pull {MAILU_IMAGE}', timeout=600)
    print(output)
    print("[OK] 镜像已拉取")
    print()

    print("[4] 创建docker-compose.yml...")
    compose_content = f'''version: '3'
services:
  mailu:
    image: {MAILU_IMAGE}
    container_name: mailu_server
    ports:
      - "25:25"
      - "587:587"
      - "465:465"
      - "8080:8080"
    environment:
      - RSPAMD_ENABLE=1
      - RELAYHOST=
      - SSL_TYPE=letsencrypt
      - ENABLE_HTTPS=0
      - DISABLE_POP3=0
      - ENABLE_MANAGESIEVE=1
    volumes:
      - mailu-data:/var/mail
      - mailu-state:/var/mail-state
    restart: unless-stopped

volumes:
  mailu-data:
  mailu-state:
'''
    run(ssh, f'cat << "EOF" | sudo tee /home/ubuntu/docker-compose.yml\n{compose_content}\nEOF')
    print("[OK] docker-compose.yml已创建")
    print()

    print("[5] 创建.env文件...")
    env_content = '''# Mailu环境配置
WEBADMIN_ENABLED=1
WEBADMIN_PASSWORD=Admin123!
SMTP_ENABLED=1
SMTP_SERVER=mailu_server
SMTP_PORT=25
FIREWALL_ENABLED=0
LOG_LEVEL=info
ENABLE_HTTPS=0
DISABLE_POP3=0
DISABLE_IMAP=1
'''
    run(ssh, f'cat << "EOF" | sudo tee /home/ubuntu/.env\n{env_content}\nEOF')
    print("[OK] .env文件已创建")
    print()

    print("[6] 启动容器...")
    output = run(ssh, 'cd /home/ubuntu && sudo docker-compose up -d', timeout=180)
    print(output)
    print()

    print("[7] 等待容器启动...")
    time.sleep(10)
    output = run(ssh, 'sudo docker ps | grep mailu')
    if output.strip():
        print(f"[OK] 容器已启动:")
        print(output)
    else:
        print("[WARNING] 容器可能未启动")
    print()

    print("[8] 检查容器日志...")
    output = run(ssh, 'sudo docker logs --tail 30 mailu_server')
    print(output)
    print()

    print("[9] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep -E "(25|587|465|8080)"')
    if output.strip():
        print("[OK] 端口正在监听:")
        print(output)
    print()

    print("[10] 配置防火墙...")
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 465/tcp')
    run(ssh, 'sudo ufw allow 8080/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("="*60)
    print("部署完成！")
    print("="*60)
    print()
    print("Mailu Web管理界面: http://49.233.89.28:8080/")
    print("管理员: admin")
    print("密码: Admin123!")
    print()
    print("SMTP 配置:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25 (SMTP) 或 587 (SUBMISSION)")
    print("  认证: 启用")
    print("  用户名: waftest")
    print("  密码: WafTest2024!")
    print("  发送者: waftest@49.233.89.28")
    print()
    print("WAF 配置:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  用户名: waftest")
    print("  密码: WafTest2024!")
    print("  认证: 启用 (PLAIN/LOGIN)")
    print()
    print("下一步:")
    print("  1. 访问Web界面创建waftest用户")
    print("  2. 在WAF中配置上述SMTP信息")
    print("  3. 发送测试邮件")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
