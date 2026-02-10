#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置虚拟域名，让Postfix支持标准邮箱格式"""
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

# 配置虚拟域名
VIRTUAL_DOMAIN = 'test-smtp.com'
VIRTUAL_HOSTNAME = 'smtp.test-smtp.com'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("配置虚拟域名 - 支持标准邮箱格式")
    print("="*60)
    print()
    print(f"  虚拟域名: {VIRTUAL_DOMAIN}")
    print(f"  主机名: {VIRTUAL_HOSTNAME}")
    print(f"  用户邮箱格式: waftest@{VIRTUAL_DOMAIN}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 配置 /etc/hosts 文件...")
    # 添加虚拟域名到 hosts 文件
    hosts_line = f"49.233.89.28  smtp.{VIRTUAL_DOMAIN} {VIRTUAL_DOMAIN}"
    run(ssh, f'echo "{hosts_line}" | sudo tee -a /etc/hosts')
    print(f"[OK] 已添加: {hosts_line}")
    print()

    print("[2] 更新Postfix配置...")
    commands = [
        f"sudo postconf -e 'myhostname = {VIRTUAL_HOSTNAME}'",
        f"sudo postconf -e 'mydomain = {VIRTUAL_DOMAIN}'",
        f"sudo postconf -e 'myorigin = {VIRTUAL_DOMAIN}'",
        f"sudo postconf -e 'mydestination = $myhostname, localhost.{VIRTUAL_DOMAIN}, localhost, $mydomain'",
    ]
    for cmd in commands:
        run(ssh, cmd)
    print(f"[OK] Postfix配置已更新使用域名: {VIRTUAL_DOMAIN}")
    print()

    print("[3] 验证配置...")
    output = run(ssh, 'sudo postconf -n | grep -E "(myhostname|mydomain|myorigin|mydestination)"')
    print(output)
    print()

    print("[4] 停止并重启Postfix...")
    run(ssh, 'sudo systemctl stop postfix')
    time.sleep(2)
    run(ssh, 'sudo systemctl start postfix')
    time.sleep(2)
    print("[OK] Postfix已重启")
    print()

    print("[5] 验证Postfix状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常")
    print()

    print("[6] 验证端口...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[7] 检查 /etc/hosts...")
    output = run(ssh, f'sudo grep {VIRTUAL_DOMAIN} /etc/hosts')
    print(output)
    print()

    print("[8] 发送测试邮件...")
    # 发送到虚拟域名的邮箱
    test_email = f"waftest@{VIRTUAL_DOMAIN}"
    run(ssh, f'echo "Test from virtual domain - $(date)" | mail -s "Virtual Domain Test" {test_email}')
    print(f"[OK] 测试邮件已发送到: {test_email}")
    print()

    print("[9] 检查邮件...")
    output = run(ssh, f'ls -la /home/waftest/Maildir/new/ 2>/dev/null || ls -la /root/Maildir/new/')
    if output.strip() and 'total' not in output.lower():
        print("[OK] 收到邮件:")
        print(output)
    else:
        print("[INFO] 邮箱为空或只有系统文件")
    print()

    print("="*60)
    print("配置完成！")
    print("="*60)
    print()
    print("WAF 防火墙 SMTP 配置信息（标准邮箱格式）：")
    print(f"  SMTP服务器: 49.233.89.28")
    print("  SMTP端口: 25")
    print(f"  用户名: waftest")
    print(f"  密码: WafTest2024!")
    print(f"  发送者邮箱: waftest@{VIRTUAL_DOMAIN}")
    print(f"  认证方式: 无（不启用）")
    print()
    print("重要提示:")
    print(f"  1. 在WAF设备中配置的邮箱必须是: waftest@{VIRTUAL_DOMAIN}")
    print(f"  2. 不要用 waftest@localhost")
    print(f"  3. 密码可以留空")
    print()
    print(f"完整邮箱: waftest@{VIRTUAL_DOMAIN}")
    print("="*60)
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
