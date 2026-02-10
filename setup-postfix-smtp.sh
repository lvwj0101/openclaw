#!/bin/bash

# ==========================================
# Postfix SMTP 服务配置脚本
# 用于测试防火墙邮件发送功能
# ==========================================

set -e

echo "========================================="
echo "Postfix SMTP 配置脚本"
echo "========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "sudo bash $0"
    exit 1
fi

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步骤1：更新系统
echo -e "${YELLOW}[1/7] 更新系统包...${NC}"
apt update
apt upgrade -y

# 步骤2：安装Postfix
echo -e "${YELLOW}[2/7] 安装Postfix...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils

# 步骤3：配置主机名
echo -e "${YELLOW}[3/7] 配置主机名...${NC}"
HOSTNAME=$(hostname)
echo "当前主机名: $HOSTNAME"

# 确保postfix配置正确
postconf -e 'myhostname = mail.flowthink.local'
postconf -e 'mydomain = flowthink.local'
postconf -e 'myorigin = $mydomain'
postconf -e 'inet_interfaces = 0.0.0.0'
postconf -e 'inet_protocols = all'
postconf -e 'mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain'
postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'
postconf -e 'home_mailbox = Maildir/'
postconf -e 'smtpd_sasl_auth_enable = no'
postconf -e 'smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'
postconf -e 'smtpd_client_restrictions = permit_mynetworks'
postconf -e 'smtpd_helo_required = yes'
postconf -e 'smtpd_helo_restrictions = permit_mynetworks'
postconf -e 'smtpd_sender_restrictions = permit_mynetworks'
postconf -e 'smtpd_recipient_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination'

# 步骤4：创建测试用户
echo -e "${YELLOW}[4/7] 创建测试用户...${NC}"
if ! id -u smtpuser &>/dev/null; then
    useradd -m -s /bin/bash smtpuser
    echo "smtpuser:SmtpTest2024!" | chpasswd
    echo -e "${GREEN}✓ 测试用户已创建: smtpuser / SmtpTest2024!${NC}"
else
    echo -e "${GREEN}✓ 测试用户已存在${NC}"
fi

# 步骤5：配置防火墙
echo -e "${YELLOW}[5/7] 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 25/tcp
    ufw allow 587/tcp
    echo -e "${GREEN}✓ 已开放 SMTP 端口: 25, 587${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 UFW，请手动开放端口 25 和 587${NC}"
fi

# 步骤6：重启Postfix服务
echo -e "${YELLOW}[6/7] 重启Postfix服务...${NC}"
systemctl restart postfix
systemctl enable postfix
systemctl status postfix --no-pager

# 步骤7：创建测试用户邮箱目录
echo -e "${YELLOW}[7/7] 创建邮箱目录...${NC}"
mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}
chown -R smtpuser:smtpuser /home/smtpuser/Maildir
chmod -R 700 /home/smtpuser/Maildir

# 验证安装
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Postfix 配置完成！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "SMTP 配置信息："
echo "-----------------------------------"
echo "SMTP 服务器: 62.234.211.119"
echo "SMTP 端口: 25 (未加密) 或 587 (可选)"
echo "用户名: smtpuser"
echo "密码: SmtpTest2024!"
echo "发送者邮箱: smtpuser@mail.flowthink.local"
echo "-----------------------------------"
echo ""

# 测试服务
echo -e "${YELLOW}测试 Postfix 服务...${NC}"
echo "Test Email from Postfix" | mail -s "Test Email" smtpuser@localhost

# 检查日志
echo ""
echo -e "${YELLOW}检查邮件日志...${NC}"
tail -n 5 /var/log/mail.log || echo "日志文件不存在"

echo ""
echo -e "${GREEN}✓ 配置完成！${NC}"
echo ""
echo "下一步："
echo "1. 在防火墙设备中使用上述 SMTP 配置"
echo "2. 发送测试邮件验证功能"
echo "3. 查看日志：tail -f /var/log/mail.log"
