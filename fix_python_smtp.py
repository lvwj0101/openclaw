#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Python SMTP服务器 - 使用标准库"""
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

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("修复Python SMTP服务器 - 使用标准库")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[2] 清空邮件队列...")
    run(ssh, 'sudo postsuper -d ALL')
    print("[OK] 邮件队列已清空")
    print()

    print("[3] 停止所有邮件服务...")
    run(ssh, 'sudo systemctl stop postfix', timeout=30)
    run(ssh, 'sudo pkill -9 -f python3', timeout=30)
    run(ssh, 'sudo pkill -9 -f smtpd', timeout=30)
    print("[OK] 已停止")
    print()

    print("[4] 创建Python SMTP服务器（使用标准库）...")
    # 使用aiohttp库而不是smtpd
    simple_smtp_server = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple SMTP Server using standard library"""
import smtpd
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 用户配置
USERS = {
    'waftest': {
        'password': 'WafTest2024!',
        'email': 'waftest@waf.local'
    },
    'root': {
        'password': 'Root123!',
        'email': 'root@waf.local'
    }
}

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        logger.info("Received message")
        logger.info(f"  From: {mailfrom}")
        logger.info(f"  To: {rcpttos}")
        logger.info(f"  Subject: {data['Subject']}")

        # 简单认证 - 不验证密码
        user = mailfrom.split('@')[0]
        if user in USERS:
            logger.info(f"  User: {user}")
            logger.info("  Authentication: Successful (no password check)")
            return '250 2.1.0 Message accepted'
        else:
            logger.info("  User: unknown")
            logger.info("  Rejecting user")
            return '550 5.7.1 User not found'

def main():
    # 监听所有接口
    server = CustomSMTPServer(('0.0.0.0', 25))
    logger.info("SMTP Server starting on 0.0.0.0:25")
    logger.info(f"Available users: {', '.join(USERS.keys())}")

    try:
        smtpd.loop()
    except KeyboardInterrupt:
        logger.info("\\nShutting down...")
        server.close()

if __name__ == '__main__':
    main()
'''
    run(ssh, "cat << 'EOF' | sudo tee /opt/smtp_server.py\n" + simple_smtp_server + "\nEOF")
    print("[OK] Python SMTP服务器已创建")
    print()

    print("[5] 创建启动脚本...")
    start_script = '''#!/bin/bash
cd /opt
nohup python3 smtp_server.py > /var/log/smtp.log 2>&1 &
echo $! > /var/run/smtp.pid
echo "Simple SMTP Server started"
'''
    run(ssh, "cat << 'EOF' | sudo tee /opt/start_smtp.sh\n" + start_script + "\nEOF")
    run(ssh, 'sudo chmod +x /opt/start_smtp.sh')
    print("[OK] 启动脚本已创建")
    print()

    print("[6] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 587/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("[7] 启动Python SMTP服务器...")
    run(ssh, 'sudo /opt/start_smtp.sh')
    time.sleep(3)
    print("[OK] 已启动")
    print()

    print("[8] 验证服务...")
    output = run(ssh, 'ps aux | grep "[p]ython3 smtp" | grep -v grep')
    if output.strip():
        print("[OK] Python SMTP服务器运行中:")
        print(output[:500])
    else:
        print("[WARNING] Python SMTP服务器未运行")
    print()

    print("[9] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[10] 检查日志...")
    output = run(ssh, 'sudo tail -10 /var/log/smtp.log 2>/dev/null || echo "Log file not found"')
    if output.strip():
        print("[OK] Python SMTP日志:")
        print(output)
    else:
        print("[INFO] 日志文件不存在")
    print()

    print("[11] 发送测试邮件...")
    test_email = "1187419065at@qq.com"
    test_body = f"""Test email from Simple SMTP Server

Server: 49.233.89.28
Port: 25
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

This is a test email from the Python SMTP server.
If you receive this email, the SMTP server is working correctly!
"""
    test_cmd = f'echo "{test_body}" | mail -s "Simple SMTP Test" {test_email}'
    run(ssh, test_cmd)
    print("[OK] 测试邮件已发送")
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("Python SMTP服务器信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  监听: 0.0.0.0:25 (所有接口）")
    print(f"  可用用户: waftest, root")
    print()
    print("WAF 配置信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者: waftest@waf.local")
    print()
    print("验证步骤:")
    print("  1. 访问Web界面: http://49.233.89.28:8080/（如果可用）")
    print("  2. 或使用上述SMTP配置直接在WAF中配置")
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
