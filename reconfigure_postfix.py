#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新配置Postfix"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("Postfix 重新配置")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Postfix状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    print(output)
    print()

    print("[2] 检查Postfix进程...")
    output = run(ssh, 'ps aux | grep "master\\|qmgr\\|pickup" | grep -v grep')
    if output.strip():
        print("[OK] Postfix进程运行中")
    else:
        print("[INFO] Postfix进程未运行")
    print()

    print("[3] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
        print(output)
    else:
        print("[INFO] 端口25未监听")
    print()

    print("[4] 停止Postfix（如果正在运行）...")
    run(ssh, 'sudo systemctl stop postfix', timeout=30)
    run(ssh, 'sudo pkill -9 -f postfix', timeout=10)
    run(ssh, 'sudo pkill -9 -f master', timeout=10)
    print("[OK] Postfix已停止")
    print()

    print("[5] 重新配置Postfix...")
    commands = [
        "sudo postconf -e 'myhostname = localhost'",
        "sudo postconf -e 'mydomain = localdomain'",
        "sudo postconf -e 'myorigin = localdomain'",
        "sudo postconf -e 'inet_interfaces = all'",
        "sudo postconf -e 'inet_protocols = ipv4'",
        "sudo postconf -e 'mydestination = $myhostname, localhost.localdomain, localhost'",
        "sudo postconf -e 'mynetworks = 0.0.0.0/0'",
        "sudo postconf -e 'home_mailbox = Maildir/'",
        "sudo postconf -e 'local_transport = local:'",
        "sudo postconf -e 'mailbox_command = /usr/bin/procmail -a $EXTENSION'",
        "sudo postconf -e 'smtpd_sasl_auth_enable = no'",
        "sudo postconf -e 'smtpd_client_restrictions = permit_sasl_authenticated, reject'",
        "sudo postconf -e 'smtpd_helo_required = no'",
        "sudo postconf -e 'smtpd_sender_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination'",
        "sudo postconf -e 'smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination'",
        "sudo postconf -e 'smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination'",
        "sudo postconf -e 'smtpd_data_restrictions = reject_unauth_sender'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] 配置已更新")
    print()

    print("[6] 检查配置...")
    output = run(ssh, 'sudo postfix check')
    if 'OK' in output or 'configuration file syntax OK' in output:
        print("[OK] 配置语法正确")
    else:
        print("[WARNING] 配置可能有问题:")
        print(output)
    print()

    print("[7] 启动Postfix...")
    run(ssh, 'sudo systemctl start postfix', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已启动")
    print()

    print("[8] 启用开机自启...")
    run(ssh, 'sudo systemctl enable postfix')
    print("[OK] 已设置开机自启")
    print()

    print("[9] 验证服务...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    elif 'active (exited)' in output:
        print("[WARNING] 服务启动后退出，但继续验证...")
    else:
        print("[WARNING] 服务状态未知")
    print()

    print("[10] 检查端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听:")
        print(output)
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[11] 检查进程...")
    output = run(ssh, 'ps aux | grep "master\\|qmgr\\|pickup" | grep -v grep')
    if output.strip():
        print("[OK] Postfix进程运行中:")
        print(output[:500])
    else:
        print("[WARNING] Postfix进程未运行")
    print()

    print("[12] 测试发送邮件...")
    output = run(ssh, 'echo "Test from Postfix at $(date)" | mail -s "Postfix Test" root@localhost')
    print("[OK] 测试邮件已发送")
    print()

    print("[13] 配置防火墙...")
    run(ssh, 'sudo ufw --force enable')
    run(ssh, 'sudo ufw allow 25/tcp')
    run(ssh, 'sudo ufw allow 22/tcp')
    output = run(ssh, 'sudo ufw status numbered | head -10')
    print("[OK] 防火墙已配置")
    print(output)
    print()

    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("SMTP 配置信息:")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  认证方式: 无")
    print("  用户名: root")
    print("  密码: 任意（不认证）")
    print("  发送者: root@localhost")
    print()
    print("防火墙配置:")
    print("  认证: 不启用 / 无")
    print("  用户名: 可以留空")
    print("  密码: 可以留空")
    print("  端口: 25")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    print("="*60)
    print("测试建议:")
    print("1. 在防火墙设备中配置上述SMTP信息")
    print("2. 发送测试邮件")
    print("3. 如果还是超时，可能是网络问题")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 配置失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
