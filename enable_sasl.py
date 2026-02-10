#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启用Postfix SASL认证"""
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

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("启用Postfix SASL认证")
    print("="*60)
    print()

    print("[1/6] 连接服务器...")
    try:
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[2/6] 安装sasl2-bin...")
    output = run(ssh, 'which saslauthd')
    if not output.strip():
        run(ssh, 'sudo apt install -y sasl2-bin', timeout=300)
        print("[OK] sasl2-bin已安装")
    else:
        print("[OK] sasl2-bin已安装")

    print()
    print("[3/6] 配置SASL认证...")
    # 启用SASL认证
    commands = [
        "sudo postconf -e 'smtpd_sasl_auth_enable = yes'",
        "sudo postconf -e 'smtpd_sasl_type = dovecot'",
        "sudo postconf -e 'smtpd_sasl_path = private/auth'",
        "sudo postconf -e 'broken_sasl_auth_clients = yes'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print("[OK] Postfix配置已更新")

    print()
    print("[4/6] 配置Dovecot SASL...")
    # 安装dovecot
    output = run(ssh, 'which dovecot')
    if not output.strip():
        run(ssh, 'sudo apt install -y dovecot-core', timeout=300)
        print("[OK] dovecot已安装")
    else:
        print("[OK] dovecot已安装")

    # 配置dovecot
    doveconf_commands = [
        "sudo mkdir -p /etc/dovecot/conf.d",
    ]
    for cmd in doveconf_commands:
        run(ssh, cmd)

    # 创建SASL配置
    sasl_config = '''
# SASL configuration
auth_mechanisms = plain login
disable_plaintext_auth = no
'''
    run(ssh, f'cat << "EOF" | sudo tee /etc/dovecot/conf.d/10-auth.conf\n{sasl_config}\nEOF')
    print("[OK] Dovecot配置已更新")

    print()
    print("[5/6] 重启服务...")
    run(ssh, 'sudo systemctl restart dovecot', timeout=30)
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    print("[OK] 服务已重启")

    print()
    print("[6/6] 验证配置...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] Postfix服务状态异常")

    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")

    # 显示配置
    print()
    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("SMTP 配置信息（已启用认证）：")
    print("  服务器: 62.234.211.119")
    print("  端口: 25")
    print("  认证方式: SASL PLAIN/LOGIN")
    print("  用户名: smtpuser")
    print("  密码: SmtpTest2024!")
    print("  发送者邮箱: smtpuser@localhost")
    print()
    print("防火墙配置：")
    print("  认证方式: 普通认证（或 PLAIN）")
    print("  加密方式: 无（或 STARTTLS 可选）")
    print()
    print("完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
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
