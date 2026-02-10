#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import time

SERVER = {
    'hostname': '62.234.211.119',
    'port': 22,
    'username': 'ubuntu',
    'password': '1qaz#EDC%TGB'
}

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SERVER, timeout=10)

    print("[1] Configure Postfix...")
    ssh.exec_command('sudo postconf -e "myhostname = localhost"')
    ssh.exec_command('sudo postconf -e "mydomain = localdomain"')
    ssh.exec_command('sudo postconf -e "inet_interfaces = all"')
    ssh.exec_command('sudo postconf -e "mynetworks = 0.0.0.0/0"')
    ssh.exec_command('sudo postconf -e "home_mailbox = Maildir/"')
    ssh.exec_command('sudo postconf -e "smtpd_sasl_auth_enable = no"')

    print("[2] Start Postfix...")
    ssh.exec_command('sudo systemctl start postfix')
    time.sleep(2)

    print("[3] Enable Postfix...")
    ssh.exec_command('sudo systemctl enable postfix')

    print("[4] Check status...")
    output = ssh.exec_command('sudo systemctl status postfix --no-pager')[1].read().decode()
    print(output)

    print("[5] Check port...")
    output = ssh.exec_command('sudo netstat -tlnp | grep :25')[1].read().decode()
    print(output)

    print("[6] Configure firewall...")
    ssh.exec_command('sudo ufw --force enable')
    ssh.exec_command('sudo ufw allow 25/tcp')

    print("[7] Test email...")
    ssh.exec_command('echo "Test" | mail -s "Test" root@localhost')

    print("\nDone! SMTP: 62.234.211.119:25 (no auth)")

    ssh.close()

if __name__ == "__main__":
    main()
