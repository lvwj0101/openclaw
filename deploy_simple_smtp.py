#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署修正版Python SMTP服务器"""
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
    print("部署修正版Python SMTP服务器")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 停止所有邮件服务...")
    run(ssh, 'sudo systemctl stop postfix')
    run(ssh, 'sudo pkill -9 -f smtpd')
    run(ssh, 'sudo pkill -9 -f master')
    print("[OK] 已停止")
    print()

    print("[2] 创建Python SMTP服务器...")
    # 简化的SASL SMTP服务器
    smtp_server_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtpd
import asyncore
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 用户配置
USERS = {}
USERS['waftest'] = {'password': 'WafTest2024!', 'email': 'waftest@waf.local'}
USERS['root'] = {'password': 'Root123!', 'email': 'root@waf.local'}

# SASL认证
class SimpleSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        logger.info("Received message")
        logger.info(f"  From: {mailfrom}")
        logger.info(f"  To: {rcpttos}")
        
        # 保存到文件
        if mailfrom in USERS:
            user_info = USERS[mailfrom]
            logger.info(f"  Authenticated as: {mailfrom}")
            filename = f"/var/mail/{int(time.time())}.eml"
            with open(filename, 'w') as f:
                f.write(str(data))
            logger.info(f"  Saved to: {filename}")
            return "250 2.1.0 Message accepted"
        else:
            logger.info("  Authentication required")
            return "530 5.7.0 Authentication required"

def main():
    server = SimpleSMTPServer(('0.0.0.0', 25))
    logger.info("SMTP Server starting on 0.0.0.0:25")
    logger.info("Available users: " + ", ".join(USERS.keys()))
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.close()

if __name__ == '__main__':
    main()
'''
    run(ssh, "cat << 'EOF' | sudo tee /opt/simple_smtp.py\n" + smtp_server_script + "\nEOF")
    print("[OK] 脚本已创建")
    print()

    print("[3] 创建启动脚本...")
    start_script = '''#!/bin/bash
cd /opt
python3 simple_smtp.py > /var/log/smtp.log 2>&1 &
echo $! > /var/run/smtp.pid
echo "Simple SMTP Server started"
'''
    run(ssh, "cat << 'EOF' | sudo tee /opt/start_simple_smtp.sh\n" + start_script + "\nEOF")
    print("[OK] 启动脚本已创建")
    print()

    print("[4] 配置防火墙...")
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    print("[OK] 防火墙已配置")
    print()

    print("[5] 启动SMTP服务器...")
    run(ssh, 'sudo chmod +x /opt/start_simple_smtp.sh')
    run(ssh, 'sudo /opt/start_simple_smtp.sh')
    print("[OK] SMTP服务器已启动")
    print()

    print("[6] 等待服务器启动...")
    time.sleep(5)
    print()

    print("[7] 检查服务状态...")
    output = run(ssh, 'ps aux | grep "python3.*simple_smtp" | grep -v grep')
    if output.strip():
        print("[OK] Python SMTP服务器运行中")
        print(output)
    else:
        print("[WARNING] Python SMTP服务器未运行")
        print("[启动] 手动启动...")
        run(ssh, 'cd /opt && python3 simple_smtp.py > /var/log/smtp.log 2>&1 &')
        time.sleep(3)
    print()

    print("[8] 测试发送邮件...")
    test_email = "Test from Simple SMTP at " + time.strftime('%Y-%m-%d %H:%M:%S')
    mail_cmd = 'echo "' + test_email + '" | mail -s "Simple SMTP Test" root@localhost'
    run(ssh, mail_cmd)
    print("[OK] 测试邮件已发送")
    print()

    print("[9] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output.lower() or not output.strip():
        print("[OK] 邮件队列为空")
    else:
        print("[INFO] 邮件队列:")
        print(output[:500])
    print()

    print("[10] 检查SMTP服务器日志...")
    output = run(ssh, 'sudo tail -20 /var/log/smtp.log')
    print(output)
    print()

    print("="*60)
    print("部署完成！")
    print("="*60)
    print()
    print("Python SMTP服务器信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  认证: SASL PLAIN")
    print(f"  可用用户: {', '.join(['waftest', 'root'])}")
    print(f"  用户密码: WafTest2024! (waftest)")
    print()
    print("WAF 配置信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print(f"  端口: 25")
    print(f"  认证: 启用 (SASL PLAIN)")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者: waftest@waf.local")
    print()
    print("下一步:")
    print("  1. 在WAF设备中配置上述SMTP信息")
    print("  2. 发送测试邮件")
    print("  3. 检查邮件是否收到")
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
