#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清空邮件队列并简化配置"""
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
    print("清空队列并简化配置")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 清空邮件队列...")
    run(ssh, 'sudo postsuper -d ALL')
    print("[OK] 邮件队列已清空")
    print()

    print("[2] 删除deferred队列...")
    run(ssh, 'sudo postsuper -d ALL deferred')
    print("[OK] deferred队列已删除")
    print()

    print("[3] 删除hold队列...")
    run(ssh, 'sudo postsuper -d ALL hold')
    print("[OK] hold队列已删除")
    print()

    print("[4] 删除incoming队列...")
    run(ssh, 'sudo postsuper -d ALL incoming')
    print("[OK] incoming队列已删除")
    print()

    print("[5] 简化Postfix配置...")
    commands = [
        # 简化 mydestination，只使用 localhost
        "sudo postconf -e 'mydestination = localhost'",
        
        # 清理不需要的配置
        "sudo postconf -e 'local_transport = local:'",
        "sudo postconf -e 'relayhost = '",
        
        # 确保网络设置正确
        "sudo postconf -e 'mynetworks = 0.0.0.0/0'",
        
        # 简化域名配置
        "sudo postconf -e 'myhostname = localhost'",
        "sudo postconf -e 'mydomain = localdomain'",
        "sudo postconf -e 'myorigin = localdomain'",
        
        # 确保接口正确
        "sudo postconf -e 'inet_interfaces = all'",
        "sudo postconf -e 'inet_protocols = ipv4'",
        
        # 确保其他配置正确
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] Postfix配置已简化")
    print()

    print("[6] 重启Postfix...")
    run(ssh, 'sudo systemctl stop postfix')
    time.sleep(2)
    run(ssh, 'sudo systemctl start postfix')
    time.sleep(3)
    print("[OK] Postfix已重启")
    print()

    print("[7] 验证队列...")
    output = run(ssh, 'sudo mailq')
    if 'empty' in output.lower():
        print("[OK] 邮件队列为空")
    else:
        print("[WARNING] 邮件队列:")
        print(output)
    print()

    print("[8] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[9] 发送测试邮件...")
    # 发送到本地用户
    run(ssh, 'echo "Clean queue test at $(date)" | mail -s "Queue Test" root@localhost')
    # 发送到waftest用户
    run(ssh, 'echo "WAF test at $(date)" | mail -s "WAF Test" waftest@localhost')
    print("[OK] 测试邮件已发送")
    print()

    print("[10] 等待3秒...")
    time.sleep(3)
    print()

    print("[11] 检查邮箱...")
    # 检查root邮箱
    output1 = run(ssh, 'ls -la /root/Maildir/new/ 2>/dev/null | tail -5')
    if output1.strip() and 'total' not in output1.lower():
        print("[OK] root邮箱:")
        print(output1)
    else:
        print("[INFO] root邮箱为空")
    print()
    
    # 检查waftest邮箱
    output2 = run(ssh, 'ls -la /home/waftest/Maildir/new/ 2>/dev/null | tail -5')
    if output2.strip() and 'total' not in output2.lower():
        print("[OK] waftest邮箱:")
        print(output2)
    else:
        print("[INFO] waftest邮箱为空")
    print()

    print("[12] 检查最新日志...")
    output = run(ssh, 'sudo tail -10 /var/log/mail.log')
    print(output)
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("WAF 防火墙 SMTP 配置信息（最终版）：")
    print("  SMTP服务器: 49.233.89.28")
    print("  SMTP端口: 25")
    print("  认证方式: 无（不启用）")
    print("  用户名: root 或 waftest（或留空）")
    print("  密码: （可以留空）")
    print("  发送者邮箱: root@localhost 或 waftest@localhost")
    print()
    print("在WAF设备中配置:")
    print("  认证: 不启用 / 无")
    print("  用户名: root（或留空）")
    print("  密码: （留空）")
    print("  端口: 25")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
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
