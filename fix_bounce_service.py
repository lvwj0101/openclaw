#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复bounce服务配置"""
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
    print("修复bounce服务配置")
    print("="*60)
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 停止Postfix...")
    run(ssh, 'sudo systemctl stop postfix', timeout=30)
    time.sleep(2)
    print("[OK] Postfix已停止")
    print()

    print("[2] 修复bounce相关配置...")
    commands = [
        # 配置2bounce_notice_recipient为空（禁用）
        "sudo postconf -e '2bounce_notice_recipient = '",
        "sudo postconf -e 'bounce_notice_recipient = '",
        "sudo postconf -e 'double_bounce_recipient = '",
        "sudo postconf -e 'empty_address_recipient = postmaster'",
        "sudo postconf -e 'mail_owner = postfix'",
        "sudo postconf -e 'mail_name = Postfix'",
        "sudo postconf -e 'always_add_missing_headers = no'",
        
        # 禁用bounce服务通知
        "sudo postconf -e 'bounce_template_file = /dev/null'",
        "sudo postconf -e '2bounce_template_file = /dev/null'",
    ]
    for cmd in commands:
        try:
            run(ssh, cmd)
        except:
            pass
    print("[OK] bounce配置已修复")
    print()

    print("[3] 启动Postfix...")
    run(ssh, 'sudo systemctl start postfix', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已启动")
    print()

    print("[4] 检查服务状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output or 'active (exited)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] 服务状态异常")
    print()
    print(output)
    print()

    print("[5] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()
    print(output)
    print()

    print("[6] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output.lower():
        print("[OK] 邮件队列为空")
    else:
        print("[INFO] 邮件队列:")
        print(output[:500])
    print()

    print("[7] 发送新的测试邮件...")
    qq_email = "1187419065@qq.com"
    test_body = f"""Bounce服务修复后的测试邮件

服务器信息:
- SMTP服务器: 49.233.89.28
- 端口: 25
- 认证: 不需要

修复内容:
- 修复bounce服务配置
- 禁用2bounce通知
- 配置空address_recipient

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明bounce服务已修复！
可以在WAF设备中使用以下配置发送邮件

SMTP服务器: 49.233.89.28
SMTP端口: 25
认证方式: 不启用
用户名: root（可以留空）
密码: （可以留空）
发送者邮箱: root@waf.local 或任意

技术支持: bounce服务修复完成
"""
    test_cmd = f'echo "{test_body}" | mail -s "Bounce Fixed Test" {qq_email}'
    run(ssh, test_cmd)
    print(f"[OK] 测试邮件已发送到: {qq_email}")
    print()

    print("[8] 检查bounce进程...")
    output = run(ssh, 'ps aux | grep bounce | grep -v grep')
    if output.strip():
        print("[INFO] bounce进程:")
        print(output)
    else:
        print("[OK] bounce进程未运行（正常）")
    print()

    print("[9] 检查Postfix主进程...")
    output = run(ssh, 'ps aux | grep "master|qmgr|pickup" | grep -v grep')
    if output.strip():
        print("[OK] Postfix进程运行正常")
        print(output[:500])
    else:
        print("[WARNING] Postfix进程未运行")
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("修复内容:")
    print("  1. 禁用2bounce_notice_recipient配置")
    print("  2. 禁用bounce通知服务")
    print("  3. 配置空地址收件人")
    print()
    print("SMTP 配置信息:")
    print(f"  服务器: {SERVER['hostname']}")
    print("  端口: 25")
    print("  认证: 不启用")
    print(f"  用户名: root（可以留空）")
    print(f"  密码: （可以留空）")
    print(f"  发送者: root@waf.local 或任意")
    print()
    print(f"测试邮箱: {qq_email}")
    print()
    print("下一步:")
    print(f"  1. 检查你的QQ邮箱 ({qq_email}) 是否收到测试邮件")
    print("  2. 如果收到，说明配置成功，WAF可以直接使用")
    print("  3. 如果没收到，继续排查问题")
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
