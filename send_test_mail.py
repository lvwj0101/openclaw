#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发送测试邮件到QQ邮箱"""
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

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='ignore')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("="*60)
    print("发送测试邮件到QQ邮箱")
    print("="*60)
    print(f"  接收邮箱: {USER_QQ_EMAIL}")
    print()

    try:
        ssh.connect(**SERVER, timeout=10)
        print("[CONNECT] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] 检查Docker容器状态...")
    output = run(ssh, 'sudo docker ps | grep mailu')
    if output.strip():
        print("[OK] Mailu容器运行中:")
        print(output)
    else:
        print("[WARNING] Mailu容器未运行")
        print("[启动] 尝试启动容器...")
        output = run(ssh, 'cd /home/ubuntu && sudo docker-compose up -d', timeout=180)
        print(output)
    print()

    print("[2] 检查端口监听...")
    output = run(ssh, 'sudo netstat -tlnp | grep -E "(25|587|465|8080)"')
    if output.strip():
        print("[OK] 端口监听:")
        print(output)
    else:
        print("[WARNING] 端口未监听")
    print()

    print("[3] 访问Mailu Web管理界面...")
    # 尝试通过curl访问Mailu API创建用户
    try:
        # 方法1: 通过API创建用户
        api_url = f"http://{SERVER['hostname']}:8080/api/v1/user/create"
        import json
        user_data = {
            'username': 'waftest',
            'password': 'WafTest2024!',
            'email': USER_QQ_EMAIL,
            'role': 'admin'
        }
        
        curl_cmd = f'curl -X POST -H "Content-Type: application/json" -d \'{json.dumps(user_data)}\' {api_url}'
        print(f"[API] 尝试创建用户...")
        output = run(ssh, curl_cmd)
        print(f"[INFO] API响应: {output}")
        
        # 检查是否创建成功
        if 'created' in output.lower() or 'success' in output.lower():
            print("[OK] 用户创建成功!")
        else:
            print("[WARNING] 用户可能未创建，继续发送测试邮件")
            
    except Exception as e:
        print(f"[WARNING] API创建用户失败: {e}")
        print("[INFO] 将使用命令行方式发送邮件")
    print()

    print("[4] 发送测试邮件...")
    # 使用mail命令发送测试邮件
    test_subject = "WAF SMTP Test Mailu Server"
    test_body = f"""
这是一个来自Mailu邮件服务器的测试邮件。

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
服务器IP: {SERVER['hostname']}
发送者: waftest@mailu

如果您收到这封邮件，说明Mailu SMTP服务器配置成功！
可以在WAF设备中使用以下配置进行邮件发送测试：

SMTP服务器: {SERVER['hostname']}
SMTP端口: 25
认证方式: SASL PLAIN/LOGIN
用户名: waftest
密码: WafTest2024!
发送者邮箱: {USER_QQ_EMAIL}

技术支持配置完成！
"""

    # 使用mail命令发送
    mail_cmd = f'echo "{test_body}" | mail -s "{test_subject}" {USER_QQ_EMAIL}'
    output = run(ssh, mail_cmd)
    print(f"[OK] 测试邮件已发送")
    print()

    print("[5] 等待3秒...")
    time.sleep(3)
    print()

    print("[6] 检查邮件队列...")
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output.lower():
        print("[OK] 邮件队列为空（邮件已投递）")
    else:
        print("[INFO] 邮件队列:")
        print(output)
    print()

    print("[7] 检查Mailu容器日志...")
    output = run(ssh, 'sudo docker logs --tail 30 mailu')
    if output.strip():
        print("[INFO] Mailu日志:")
        print(output)
    print()

    print("[8] 发送第二封测试邮件（使用echo管道）...")
    mail_cmd2 = f'echo "Second test from Mailu at $(date)" | mail -s "Mailu SMTP Test 2" {USER_QQ_EMAIL}'
    output = run(ssh, mail_cmd2)
    print(f"[OK] 第二封测试邮件已发送")
    print()

    print("[9] 再次检查队列...")
    time.sleep(2)
    output = run(ssh, 'sudo mailq')
    if 'Mail queue is empty' in output.lower():
        print("[OK] 邮件队列为空")
    else:
        print("[INFO] 邮件队列:")
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
    print("下一步:")
    print("  1. 请登录你的QQ邮箱: {USER_QQ_EMAIL}")
    print("  2. 查看收件箱（或垃圾邮件箱）")
    print("  3. 确认是否收到测试邮件")
    print()
    print("如果你收到了这封邮件，说明Mailu SMTP服务器配置成功！")
    print("WAF设备可以使用以下SMTP配置:")
    print(f"  服务器: {SERVER['hostname']}")
    print("  端口: 25")
    print("  认证: SASL PLAIN/LOGIN")
    print("  用户名: waftest")
    print("  密码: WafTest2024!")
    print(f"  发送者: {USER_QQ_EMAIL}")
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
