#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器连接
"""

import paramiko
import sys
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 服务器配置
SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': 'ji_pmrDc6jMCc6_'
}

def main():
    print("[TEST] 测试服务器连接...")
    print(f"   地址: {SERVER['username']}@{SERVER['hostname']}:{SERVER['port']}")
    print()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("[CONNECT] 正在连接...")
        ssh.connect(**SERVER, timeout=10)
        print("[OK] 连接成功！")
        print()

        # 测试命令1: hostname
        print("[CMD1] 执行 hostname...")
        stdin, stdout, stderr = ssh.exec_command('hostname', timeout=10)
        output = stdout.read().decode('utf-8').strip()
        print(f"[OK] hostname: {output}")
        print()

        # 测试命令2: whoami
        print("[CMD2] 执行 whoami...")
        stdin, stdout, stderr = ssh.exec_command('whoami', timeout=10)
        output = stdout.read().decode('utf-8').strip()
        print(f"[OK] whoami: {output}")
        print()

        # 测试命令3: 检查Postfix
        print("[CMD3] 检查Postfix...")
        stdin, stdout, stderr = ssh.exec_command('which postfix', timeout=10)
        output = stdout.read().decode('utf-8').strip()
        if output:
            print(f"[OK] Postfix已安装: {output}")
        else:
            print("[INFO] Postfix未安装")
        print()

        # 测试命令4: 检查防火墙
        print("[CMD4] 检查UFW状态...")
        stdin, stdout, stderr = ssh.exec_command('sudo ufw status', timeout=10)
        output = stdout.read().decode('utf-8')
        print(output)
        print()

        print("=" * 60)
        print("[SUCCESS] 所有测试通过！服务器连接正常")
        print("=" * 60)

        return 0

    except paramiko.AuthenticationException:
        print("[ERROR] 认证失败：用户名或密码错误")
        return 1
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
