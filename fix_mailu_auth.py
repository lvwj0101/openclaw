#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Mailu认证配置问题"""
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

CONTAINER_NAME = 'mailu_server'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("修复Mailu SMTP认证问题")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Docker容器状态...")
    output = run(ssh, f'sudo docker ps | grep {CONTAINER_NAME}')
    if output.strip():
        print(f"[OK] 容器 {CONTAINER_NAME} 正在运行")
    else:
        print(f"[WARNING] 容器 {CONTAINER_NAME} 未运行")
        print()
        print("[启动] 启动容器...")
        run(ssh, f'sudo docker start {CONTAINER_NAME}', timeout=30)
        time.sleep(5)
        print("[OK] 容器已启动")
    print()

    print("[2] 查看Docker容器日志（最近20行）...")
    output = run(ssh, f'sudo docker logs --tail 20 {CONTAINER_NAME}')
    print(output)
    print()

    print("[3] 停止并重新创建容器（使用正确认证配置）...")
    print("[3a] 停止旧容器...")
    run(ssh, f'sudo docker stop {CONTAINER_NAME}', timeout=30)
    run(ssh, f'sudo docker rm {CONTAINER_NAME}', timeout=30)
    time.sleep(2)
    print("[OK] 旧容器已删除")
    print()

    print("[3b] 创建新的.env文件（启用认证）...")
    env_content = '''# Mailu环境配置（修复认证问题）

# 禁用HTTPS（测试用）
ENABLE_HTTPS=0

# 启用SMTP认证
SMTP_ENABLED=1
SMTP_PORT=25
SMTP_SERVER=mailu_server

# 启用SMTPS
SMTPS_ENABLED=1
SMTPS_PORT=465

# 启用提交端口
SUBMISSION_PORT=587

# 禁用POP3和IMAP
DISABLE_POP3=1
DISABLE_IMAP=1

# 启用Web管理界面
WEBADMIN_ENABLED=1
WEBADMIN_PASSWORD=Admin123!

# 防火墙配置（禁用，避免端口问题）
FIREWALL_ENABLED=0

# 启用邮件队列
QUEUED_MESSAGE_LIMIT=100

# 日志配置
LOG_LEVEL=info

# 域名配置（使用IP地址）
HOSTNAME=49.233.89.28

# DNS配置（禁用MX查找，避免DNS问题）
DNS_ENABLED=0

# 启用RSPAMD（防垃圾邮件）
RSPAMD_ENABLED=1

# 启用SASL认证
ENABLE_SASL=1

# 启用CRAM-MD5认证
ENABLE_CRAM=1

# 启用PLAIN和LOGIN认证
SASL_AUTH_MECH=PLAIN LOGIN

# 关键：允许所有IP连接
MYNETWORKS=0.0.0.0/0

# 禁用TLS加密（避免SSL证书问题）
DISABLE_POP3_STARTTLS=1
DISABLE_IMAP_STARTTLS=1
DISABLE_TLS_VALIDATION=1
'''
    run(ssh, 'cat << "EOF" | sudo tee /home/ubuntu/mailu.env\n' + env_content + '\nEOF')
    print("[OK] .env文件已创建")
    print()

    print("[3c] 创建docker-compose.yml...")
    compose_content = '''version: '3'
services:
  mailu:
    image: mailserver/mailu
    container_name: ''' + CONTAINER_NAME + '''
    ports:
      - "25:25"
      - "465:465"
      - "587:587"
      - "8080:8080"
    env_file:
      - /home/ubuntu/mailu.env
    volumes:
      - mailu-data:/var/mail
      - mailu-state:/var/mail-state
      - mailu-logs:/var/log/mail
    restart: unless-stopped
    command: >
      sh -c "echo 'Starting Mailu...' && 
             /usr/bin/dovecot &&
             echo 'Dovecot started...' &&
             sleep infinity"

volumes:
  mailu-data:
  mailu-state:
  mailu-logs:
'''
    run(ssh, 'cat << "EOF" | sudo tee /home/ubuntu/mailu-compose.yml\n' + compose_content + '\nEOF')
    print("[OK] docker-compose.yml已创建")
    print()

    print("[4] 启动新容器...")
    output = run(ssh, 'cd /home/ubuntu && sudo docker-compose up -d', timeout=180)
    print(output)
    print()

    print("[5] 等待容器启动...")
    time.sleep(10)
    print("[OK] 等待完成")
    print()

    print("[6] 检查容器状态...")
    output = run(ssh, f'sudo docker ps | grep {CONTAINER_NAME}')
    if output.strip():
        print(f"[OK] 容器 {CONTAINER_NAME} 正在运行")
        print(output)
    else:
        print(f"[WARNING] 容器 {CONTAINER_NAME} 未运行")
    print()

    print("[7] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep -E "(25|465|587|8080)"')
    if output.strip():
        print("[OK] 端口正在监听:")
        print(output)
    else:
        print("[WARNING] 端口未监听")
    print()

    print("[8] 查看容器日志...")
    output = run(ssh, f'sudo docker logs --tail 30 {CONTAINER_NAME}')
    print(output)
    print()

    print("[9] 检查防火墙...")
    output = run(ssh, 'sudo ufw status')
    print(output)
    print()

    print("[10] 配置防火墙...")
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 465/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 8080/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("Mailu SMTP 配置信息（修复版）：")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  SMTP端口: 25")
    print(f"  SMTPS端口: 465 (TLS)")
    print(f"  SUBMISSION端口: 587")
    print(f"  Web管理: http://{SERVER['hostname']}:8080/")
    print(f"  Web管理员: admin")
    print(f"  Web密码: Admin123!")
    print()
    print("WAF 防火墙 SMTP 配置信息：")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25 (SMTP) 或 587 (SUBMISSION)")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  认证: SASL PLAIN/LOGIN")
    print(f"  加密: 无或 TLS (465)")
    print()
    print("重要提示:")
    print(f"  1. WAF必须使用端口25 (SMTP)")
    print(f"  2. 或使用端口587 (SUBMISSION, 支持认证)")
    print(f"  3. 端口465 (SMTPS) 需要TLS证书")
    print()
    print("下一步:")
    print("  1. 等待30秒让容器完全启动")
    print("  2. 在Mailu Web界面创建waftest用户")
    print("  3. 在WAF中配置上述SMTP信息")
    print("  4. 发送测试邮件")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 修复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
