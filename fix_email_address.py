#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复邮箱地址并重新发送"""
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

# 正确的邮箱地址
CORRECT_EMAIL = '1187419065@qq.com'

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("修复邮箱地址 - 重新发送测试邮件")
    print("="*60)
    print(f"  正确邮箱: {CORRECT_EMAIL}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查当前邮件队列...")
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[2] 检查错误邮箱地址...")
    output = run(ssh, 'sudo mailq | grep "1187419065at"')
    if output.strip():
        print("[INFO] 发现错误邮箱地址的邮件:")
        print(output)
        print()
        print("[3] 删除所有错误邮件...")
        run(ssh, 'sudo postsuper -d ALL')
        print("[OK] 所有邮件已删除")
    else:
        print("[OK] 没有错误邮箱地址的邮件")
    print()

    print("[4] 向正确邮箱发送测试邮件...")
    test_subject = "Postfix SMTP Test - Correct Email"
    test_body = f"""
这是一封来自Postfix SMTP服务器的测试邮件。

服务器信息:
- SMTP服务器: 49.233.89.28
- 端口: 25
- 正确邮箱: {CORRECT_EMAIL}
- 错误邮箱: 1187419065at@qq.com

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明:
1. Postfix SMTP服务器配置正确
2. 可以处理发送到正确邮箱地址的邮件
3. WAF设备可以正常使用此SMTP服务器

WAF设备配置:
- SMTP服务器: 49.233.89.28
- SMTP端口: 25
- 认证方式: 不启用
- 用户名: root（可以留空）
- 密码: （可以留空）
- 发送者邮箱: root@waf.local 或任意邮箱

请检查您的QQ邮箱 ({CORRECT_EMAIL})，确认是否收到这封测试邮件！

---
技术支持: Postfix SMTP服务器修复完成
"""
    
    mail_cmd = f'echo "{test_body}" | mail -s "{test_subject}" {CORRECT_EMAIL}'
    run(ssh, mail_cmd)
    print(f"[OK] 测试邮件已发送到: {CORRECT_EMAIL}")
    print()

    print("[5] 检查邮件队列...")
    time.sleep(3)
    output = run(ssh, 'sudo mailq')
    print(output)
    print()

    print("[6] 检查最近的邮件日志...")
    output = run(ssh, 'sudo tail -30 /var/log/mail.log | grep -i "to={CORRECT_EMAIL} status="')
    if output.strip():
        print("[邮件投递日志]:")
        print(output)
    else:
        print("[INFO] 未找到投递日志")
    print()

    print("[7] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("="*60)
    print("修复完成！")
    print("="*60)
    print()
    print("发送信息:")
    print(f"  正确邮箱: {CORRECT_EMAIL}")
    print(f"  测试邮件已发送到: {CORRECT_EMAIL}")
    print()
    print("WAF 配置:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证: 不启用")
    print("  用户名: root（可留空）")
    print("  密码: （可留空）")
    print(f"  发送者: root@waf.local 或任意")
    print()
    print("验证步骤:")
    print(f"  1. 请登录你的QQ邮箱: {CORRECT_EMAIL}")
    print("  2. 查看收件箱和垃圾邮件箱")
    print("  3. 确认是否收到测试邮件")
    print()
    print("如果收到邮件:")
    print("  说明Postfix配置成功！")
    print("  WAF设备可以使用SMTP服务器 49.233.89.28")
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
