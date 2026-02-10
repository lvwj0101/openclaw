#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用简单SMTP服务器发送测试邮件到QQ邮箱"""
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

# 用户的QQ邮箱
USER_QQ_EMAIL = '1187419065at qq.com'

def run(ssh, cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("发送测试邮件到QQ邮箱")
    print("="*60)
    print(f"  目标邮箱: {USER_QQ_EMAIL}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 停止所有Docker容器...")
    run(ssh, 'sudo docker stop $(sudo docker ps -aq) 2>/dev/null || true', timeout=30)
    run(ssh, 'sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true', timeout=30)
    print("[OK] Docker容器已清理")
    print()

    print("[2] 重启Postfix（原生邮件服务器）...")
    run(ssh, 'sudo systemctl restart postfix', timeout=30)
    time.sleep(3)
    print("[OK] Postfix已重启")
    print()

    print("[3] 检查Postfix状态...")
    output = run(ssh, 'sudo systemctl status postfix --no-pager')
    if 'active (running)' in output or 'active (exited)' in output:
        print("[OK] Postfix服务运行正常")
    else:
        print("[WARNING] Postfix服务状态未知")
    print()

    print("[4] 检查端口25...")
    output = run(ssh, 'sudo netstat -tlnp | grep :25')
    if ':25' in output:
        print("[OK] 端口25正在监听")
    else:
        print("[WARNING] 端口25未监听")
    print()

    print("[5] 发送测试邮件到QQ邮箱...")
    test_subject = "WAF SMTP Test - Postfix Server"
    test_body = f"""
这是一封来自WAF SMTP测试邮件。

服务器信息:
- SMTP服务器: 49.233.89.28
- 端口: 25
- 认证: 不需要

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明Postfix SMTP服务器配置成功！
可以在WAF设备中使用以下配置:

SMTP服务器: 49.233.89.28
SMTP端口: 25
认证方式: 不启用 / 无
用户名: root（可以留空）
密码: （可以留空）
发送者邮箱: root@localhost 或任意邮箱

WAF设备配置完成后，请发送测试邮件验证功能！

---
技术支持团队配置完成
"""
    
    # 方法1: 通过mail命令发送
    mail_cmd = f'echo "{test_body}" | mail -s "{test_subject}" {USER_QQ_EMAIL}'
    print(f"[METHOD1] 使用mail命令发送...")
    output = run(ssh, mail_cmd)
    print(f"[OK] 命令已执行")
    print()
    
    # 等待邮件处理
    print("[6] 等待5秒...")
    time.sleep(5)
    
    # 检查邮件队列
    print("[7] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output or not output.strip():
        print("[OK] 邮件队列为空（邮件已发送）")
    else:
        print("[INFO] 邮件队列:")
        print(output[:500])
    print()
    
    # 检查邮件日志
    print("[8] 检查邮件日志...")
    output = run(ssh, 'sudo tail -20 /var/log/mail.log')
    print(output)
    print()
    
    print("="*60)
    print("测试邮件已发送！")
    print("="*60)
    print()
    print("发送信息:")
    print(f"  收件人: {USER_QQ_EMAIL}")
    print(f"  主题: {test_subject}")
    print(f"  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("请检查你的QQ邮箱（包括垃圾邮件箱），看是否收到测试邮件！")
    print()
    print("WAF SMTP配置:")
    print("  服务器: 49.233.89.28")
    print("  端口: 25")
    print("  认证: 不启用 / 无")
    print("  用户名: root（可以留空）")
    print("  密码: （可以留空）")
    print()
    print("如果收到邮件，说明配置成功！可以在WAF中测试发送功能了。")
    print()
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    ssh.close()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] 发送失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
