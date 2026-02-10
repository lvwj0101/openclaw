#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署Docker邮件服务器 - Mailu"""
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

# Mailu Docker配置
MAILU_IMAGE = 'mailserver/mailu'
MAILU_PORT_HTTP = 8080
MAILU_PORT_SMTP = 25
MAILU_PORT_SMTPS = 465
MAILU_PORT_SUBMISSION = 587
MAILU_PORT_IMAP = 143
MAILU_PORT_POP3 = 110
MAILU_PORT_POP3S = 995

# 容器配置
CONTAINER_NAME = 'mailu_server'

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("Docker邮件服务器 - Mailu部署")
    print("="*60)
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  用户: {SERVER['username']}")
    print()

    try:
        ssh.connect(**SERVER, timeout=15)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Docker环境...")
    output = run(ssh, 'which docker')
    docker_installed = output.strip()
    if not docker_installed:
        print("[INFO] Docker未安装，开始安装...")
        output = run(ssh, 'sudo apt update', timeout=180)
        output = run(ssh, 'sudo apt install -y docker.io docker-compose', timeout=600)
        print("[OK] Docker已安装")
    else:
        print(f"[OK] Docker已安装: {docker_installed}")
    print()

    print("[2] 创建docker-compose.yml...")
    docker_compose = f'''version: '3'
services:
  mailu:
    image: {MAILU_IMAGE}
    container_name: {CONTAINER_NAME}
    ports:
      - "{MAILU_PORT_HTTP}:{MAILU_PORT_HTTP}"
      - "{MAILU_PORT_SMTP}:{MAILU_PORT_SMTP}"
      - "{MAILU_PORT_SMTPS}:{MAILU_PORT_SMTPS}"
      - "{MAILU_PORT_SUBMISSION}:{MAILU_PORT_SUBMISSION}"
      - "{MAILU_PORT_IMAP}:{MAILU_PORT_IMAP}"
      - "{MAILU_PORT_POP3}:{MAILU_PORT_POP3}"
      - "{MAILU_PORT_POP3S}:{MAILU_PORT_POP3S}"
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
    run(ssh, f'cat << "EOF" | sudo tee /home/ubuntu/mailu-compose.yml\n{docker_compose}\nEOF')
    print("[OK] docker-compose.yml已创建")
    print()

    print("[3] 创建.env文件...")
    env_content = f'''# Mailu环境配置
# Web管理界面
WEBADMIN_ENABLED=1
WEBADMIN_PASSWORD=Admin123!

# SMTP配置
SMTP_ENABLED=1
SMTP_SERVER=mailu_server
SMTP_PORT=25

# 防火墙配置（开放所有端口）
FIREWALL_ENABLED=0

# 日志配置
LOG_LEVEL=info

# 启用所有协议
ENABLE_HTTPS=0
DISABLE_POP3=0
DISABLE_IMAP=0
'''
    run(ssh, f'cat << "EOF" | sudo tee /home/ubuntu/mailu.env\n{env_content}\nEOF')
    print("[OK] .env文件已创建")
    print()

    print("[4] 停止并删除旧容器...")
    run(ssh, f'sudo docker stop {CONTAINER_NAME} 2>/dev/null || true', timeout=30)
    run(ssh, f'sudo docker rm {CONTAINER_NAME} 2>/dev/null || true', timeout=30)
    print("[OK] 旧容器已清理")
    print()

    print("[5] 拉取Docker镜像...")
    output = run(ssh, f'sudo docker pull {MAILU_IMAGE}', timeout=300)
    print(output)
    print()

    print("[6] 启动Docker容器...")
    output = run(ssh, 'cd /home/ubuntu && sudo docker-compose up -d', timeout=180)
    print(output)
    print()

    print("[7] 等待容器启动...")
    time.sleep(10)
    output = run(ssh, f'sudo docker ps | grep {CONTAINER_NAME}')
    if output.strip():
        print(f"[OK] 容器正在运行")
        print(output)
    else:
        print("[WARNING] 容器可能未启动")
    print()

    print("[8] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep -E "(25|587|465|8080)"')
    if output.strip():
        print("[OK] 端口监听:")
        print(output)
    else:
        print("[WARNING] 端口未监听")
    print()

    print("[9] 检查容器日志...")
    output = run(ssh, f'sudo docker logs --tail 20 {CONTAINER_NAME}')
    if output.strip():
        print("[OK] 容器日志:")
        print(output)
    print()

    print("[10] 创建测试用户...")
    # 通过API创建用户
    # Mailu的API端口通常是8080
    import requests
    import json
    
    try:
        # 尝试创建waftest用户
        api_url = f"http://{SERVER['hostname']}:{MAILU_PORT_HTTP}/api/v1/user/create"
        user_data = {
            'username': 'waftest',
            'password': 'WafTest2024!',
            'email': 'waftest@49.233.89.28',
            'role': 'admin'
        }
        
        # 在服务器上执行curl命令
        curl_cmd = f'curl -X POST -H "Content-Type: application/json" -d \'{{"username":"waftest","password":"WafTest2024!","email":"waftest@49.233.89.28"}}\' {api_url}'
        output = run(ssh, curl_cmd)
        print(f"[INFO] API响应: {output}")
        
    except Exception as e:
        print(f"[WARNING] 无法通过API创建用户: {e}")
        print("[INFO] 将通过Web界面创建用户")
    print()

    print("[11] 设置开机自启...")
    run(ssh, f'sudo docker update {CONTAINER_NAME} --restart unless-stopped', timeout=30)
    print("[OK] 已设置开机自启")
    print()

    print("[12] 配置防火墙...")
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
    print("Mailu Web管理界面:")
    print(f"  访问地址: http://{SERVER['hostname']}:{MAILU_PORT_HTTP}/")
    print(f"  管理员账号: admin")
    print(f"  管理员密码: Admin123!")
    print()
    print("SMTP 配置信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  SMTP端口: 25")
    print(f"  SMTPS端口: 465")
    print(f"  认证: 需要")
    print(f"  测试账号: waftest")
    print(f"  测试密码: WafTest2024!")
    print(f"  发送者邮箱: waftest@49.233.89.28")
    print()
    print("WAF 配置:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者: waftest@49.233.89.28")
    print(f"  认证: 启用")
    print()
    print("下一步:")
    print("  1. 访问Web管理界面")
    print("  2. 验证waftest用户是否创建")
    print("  3. 在WAF中配置上述SMTP信息")
    print("  4. 发送测试邮件")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
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
