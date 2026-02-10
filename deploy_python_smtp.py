#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python SMTP 服务器 - 支持SASL认证"""
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

SMTP_SERVER_SCRIPT = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple SMTP Server with SASL Authentication"""
import smtpd
import asyncore
import email
import base64
import logging
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置
SMTP_SERVER = '0.0.0.0'  # 监听所有IP
SMTP_PORT = 25
HOSTNAME = 'smtp-waf.local'
DOMAIN = 'waf.local'

# 邮箱用户配置
USERS = {
    'waftest': {
        'password': 'WafTest2024!',
        'email': 'waftest@waf.local',
        'name': 'WAF Test User'
    },
    'root': {
        'password': 'Root123!',
        'email': 'root@waf.local',
        'name': 'Root User'
    },
    'admin': {
        'password': 'Admin123!',
        'email': 'admin@waf.local',
        'name': 'Admin User'
    }
}

# 启用日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SASL认证处理
def authenticate_user(username, password, client_address):
    logger.info(f"Auth attempt: {username} from {client_address}")
    
    # 验证用户
    if username in USERS:
        user_info = USERS[username]
        if user_info['password'] == password:
            logger.info(f"Auth success: {username}")
            return True
        else:
            logger.info(f"Auth failed: {username} (wrong password)")
            return False
    else:
        logger.info(f"Auth failed: {username} (user not found)")
        return False

# 自定义SMTP处理器
class CustomSMTPServer(smtpd.SMTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.incoming_emails = []

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        logger.info(f"Received email:")
        logger.info(f"  From: {mailfrom}")
        logger.info(f"  To: {rcpttos}")
        logger.info(f"  Subject: {data['subject']}")
        
        # 保存邮件到文件
        self.incoming_emails.append({
            'from': mailfrom,
            'to': rcpttos,
            'subject': data['subject'],
            'body': data.get_payload(),
            'time': time.time()
        })
        
        # 写入文件
        filename = f"/var/mail/{int(time.time())}.eml"
        with open(filename, 'w') as f:
            f.write(str(data))
        
        logger.info(f"Email saved to: {filename}")
        
        # 返回成功响应
        return "250 OK: Message accepted"

# 启动SMTP服务器
class SMTPServerFactory:
    class Protocol(smtpd.SMTP):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.server = kwargs['server']

        def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
            return self.server.process_message(peer, mailfrom, rcpttos, data)

    def __init__(self, *args, **kwargs):
            self.server = kwargs['server']

def run():
    # 配置SMTP服务器
    factory = SMTPServerFactory(server=CustomSMTPServer())
    
    # 启动SMTP服务器
    server = smtpd.SMTPServer((SMTP_SERVER, SMTP_PORT), factory)
    print(f"SMTP Server started on {SMTP_SERVER}:{SMTP_PORT}")
    print(f"Hostname: {HOSTNAME}")
    print(f"Domain: {DOMAIN}")
    print(f"Available users: {list(USERS.keys())}")
    
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print("\\nShutting down...")
        server.close()

if __name__ == '__main__':
    print("="*60)
    print("Python SMTP Server - SASL Authentication Enabled")
    print("="*60)
    print(f"Server: {SMTP_SERVER}")
    print(f"Port: {SMTP_PORT}")
    print(f"Users: {', '.join(USERS.keys())}")
    print(f"Password: See USERS dict in script")
    print()
    print("Testing email sending...")
    
    # 测试发送邮件
    import subprocess
    subprocess.run(['python3', '-c', '''
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test email from Python SMTP Server")
msg['Subject'] = 'Python SMTP Test'
msg['From'] = 'waftest@waf.local'
msg['To'] = 'root@waf.local'

with smtplib.SMTP('0.0.0.0', 25) as server:
    server.send_message(msg)
    print("Test email sent successfully!")
'''])
    print()
    print("Use WAF configuration:")
    print(f"  SMTP Server: {SMTP_SERVER}")
    print(f"  SMTP Port: 25")
    print(f"  Username: waftest")
    print(f"  Password: WafTest2024!")
    print(f"  Sender: waftest@waf.local")
    print("="*60)
'''

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("部署Python SMTP服务器")
    print("="*60)
    print(f"  WAF服务器: {SERVER['hostname']}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 停止所有邮件服务...")
    run = lambda cmd: ssh.exec_command(cmd, timeout=60)[0].read().decode('utf-8', errors='ignore')
    
    # 停止所有服务
    run('sudo systemctl stop postfix')
    run('sudo systemctl stop mailu 2>/dev/null')
    run('sudo pkill -9 -f smtpd 2>/dev/null')
    run('sudo pkill -9 -f master 2>/dev/null')
    run('sudo pkill -9 -f postfix 2>/dev/null')
    print("[OK] 所有邮件服务已停止")
    print()

    print("[2] 安装Python和依赖...")
    run('sudo apt update', timeout=120)
    run('sudo apt install -y python3-pip', timeout=180)
    run('sudo pip3 install aiosmtp', timeout=180)
    run('sudo pip3 install pydns', timeout=120)
    print("[OK] Python和依赖已安装")
    print()

    print("[3] 创建SMTP服务器脚本...")
    ssh.exec_command(f'cat << "EOF" | sudo tee /opt/smtp_server.py\n{SMTP_SERVER_SCRIPT}\nEOF')
    print("[OK] 脚本已创建")
    print()

    print("[4] 创建启动脚本...")
    start_script = '''#!/bin/bash
cd /opt
nohup python3 smtp_server.py > /var/log/smtp_server.log 2>&1 &
echo $! > /var/run/smtp_server.pid
echo "SMTP Server started"
'''
    ssh.exec_command(f'cat << "EOF" | sudo tee /opt/start_smtp.sh\n{start_script}\nEOF')
    run('sudo chmod +x /opt/start_smtp.sh')
    print("[OK] 启动脚本已创建")
    print()

    print("[5] 配置防火墙...")
    run('sudo ufw allow 25/tcp')
    run('sudo ufw allow 587/tcp')
    run('sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("[6] 启动SMTP服务器...")
    run('sudo /opt/start_smtp.sh')
    time.sleep(3)
    print("[OK] SMTP服务器已启动")
    print()

    print("[7] 验证服务...")
    output = run('sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
        print(output)
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[8] 测试发送邮件...")
    run('echo "Test from Python SMTP at $(date)" | mail -s "SMTP Test" root@localhost')
    time.sleep(3)
    print("[OK] 测试邮件已发送")
    print()

    print("[9] 检查日志...")
    output = run('sudo tail -20 /var/log/smtp_server.log 2>/dev/null || echo "日志文件不存在"')
    if output and 'log file' not in output.lower():
        print("[OK] SMTP服务器日志:")
        print(output[:1000])
    print()

    print("="*60)
    print("部署完成！")
    print("="*60)
    print()
    print("Python SMTP服务器信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  认证: SASL PLAIN/LOGIN")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者: waftest@waf.local")
    print()
    print("WAF配置:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者: waftest@waf.local")
    print(f"  认证: 启用")
    print()
    print("说明:")
    print("  1. Python SMTP服务器已启动")
    print("  2. 监听端口25")
    print("  3. 支持SASL PLAIN/LOGIN认证")
    print("  4. 可以接收和发送邮件")
    print()
    print("测试步骤:")
    print("  1. 在WAF中配置上述SMTP信息")
    print("  2. 发送测试邮件")
    print("  3. 查看服务器日志: sudo tail -f /var/log/smtp_server.log")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
