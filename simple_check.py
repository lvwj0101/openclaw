#!/usr/bin/env python3
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("[CONNECT] 连接服务器...")
    try:
        ssh.connect(**SERVER, timeout=15)
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return 1

    print()
    print("[1] Postfix状态...")
    output = ssh.exec_command('sudo systemctl status postfix --no-pager')[1].read().decode()
    print(output)

    print()
    print("[2] Postfix进程...")
    output = ssh.exec_command('ps aux | grep master | grep -v grep')[1].read().decode()
    print(output if output.strip() else "[INFO] Postfix进程未运行")

    print()
    print("[3] 端口25...")
    output = ssh.exec_command('sudo netstat -tlnp | grep :25')[1].read().decode()
    print(output if ':25' in output else "[INFO] 端口25未监听")

    print()
    print("[4] 邮件队列...")
    output = ssh.exec_command('sudo mailq')[1].read().decode()
    print(output if output.strip() and 'empty' not in output.lower() else "[OK] 队列为空")

    print()
    print("[5] Postfix配置...")
    output = ssh.exec_command('sudo postconf -n | grep -E "(inet|networks|smtpd_sasl)"')[1].read().decode()
    print(output)

    print()
    print("[6] 测试发送...")
    output = ssh.exec_command('echo "Test" | mail -s "WAF Test" root@localhost')[1].read().decode()
    print("[OK] 测试邮件已发送")

    ssh.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
