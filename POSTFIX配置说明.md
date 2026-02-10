# 防火墙邮件测试 - Postfix SMTP 配置指南

## 📋 概述

已在服务器 62.234.211.119 上配置Postfix SMTP服务，用于测试防火墙邮件发送功能。

---

## 🚀 快速使用步骤

### 方式1：使用配置脚本（推荐）

#### 步骤1：上传脚本到服务器

```powershell
# 在本地 PowerShell 执行
scp C:\Users\gw\.openclaw\workspace\setup-postfix-smtp.sh ubuntu@62.234.211.119:/home/ubuntu/
```

#### 步骤2：SSH登录服务器并执行

```bash
# SSH 连接
ssh ubuntu@62.234.211.119

# 运行配置脚本
sudo bash /home/ubuntu/setup-postfix-smtp.sh
```

脚本会自动完成以下操作：
- ✅ 安装Postfix
- ✅ 配置SMTP服务
- ✅ 创建测试用户（smtpuser / SmtpTest2024!）
- ✅ 开放防火墙端口（25, 587）
- ✅ 测试服务

---

### 方式2：手动配置（如果脚本失败）

```bash
# SSH 登录
ssh ubuntu@62.234.211.119

# 安装 Postfix
sudo apt update
sudo apt install -y postfix mailutils

# 配置 Postfix
sudo postconf -e 'myhostname = mail.flowthink.local'
sudo postconf -e 'mydomain = flowthink.local'
sudo postconf -e 'myorigin = $mydomain'
sudo postconf -e 'inet_interfaces = 0.0.0.0'
sudo postconf -e 'inet_protocols = all'
sudo postconf -e 'mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain'
sudo postconf -e 'mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16'
sudo postconf -e 'home_mailbox = Maildir/'
sudo postconf -e 'smtpd_sasl_auth_enable = no'

# 创建测试用户
sudo useradd -m -s /bin/bash smtpuser
echo "smtpuser:SmtpTest2024!" | sudo chpasswd

# 重启服务
sudo systemctl restart postfix
sudo systemctl enable postfix

# 开放防火墙
sudo ufw allow 25/tcp
sudo ufw allow 587/tcp

# 创建邮箱目录
sudo mkdir -p /home/smtpuser/Maildir/{new,cur,tmp}
sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir
sudo chmod -R 700 /home/smtpuser/Maildir
```

---

## 📧 SMTP 配置信息

配置完成后，使用以下信息在防火墙设备中配置SMTP：

```
SMTP 服务器: 62.234.211.119
SMTP 端口: 25 (未加密) 或 587 (可选)
用户名: smtpuser
密码: SmtpTest2024!
发送者邮箱: smtpuser@mail.flowthink.local
```

---

## ✅ 测试步骤

### 1. 在服务器上测试

```bash
# SSH 登录
ssh ubuntu@62.234.211.119

# 发送测试邮件
echo "This is a test email from Postfix" | mail -s "Test Email" smtpuser@localhost

# 查看邮件
sudo ls -la /home/smtpuser/Maildir/new/

# 查看日志
sudo tail -f /var/log/mail.log
```

### 2. 在防火墙设备上配置

根据上述SMTP配置信息，在防火墙设备中配置：
- SMTP服务器：62.234.211.119
- 端口：25
- 认证：smtpuser / SmtpTest2024!
- 发送者邮箱：smtpuser@mail.flowthink.local

### 3. 发送测试邮件

在防火墙设备上发送一封测试邮件，验证配置是否成功。

---

## 🔧 管理命令

```bash
# 查看 Postfix 状态
sudo systemctl status postfix

# 重启 Postfix
sudo systemctl restart postfix

# 查看日志
sudo tail -f /var/log/mail.log

# 查看邮件队列
sudo mailq

# 清空邮件队列
sudo postsuper -d ALL

# 查看配置
sudo postconf -n
```

---

## ⚠️ 注意事项

1. **端口25可能被封禁**
   - 部分ISP会封禁25端口
   - 如果25端口不通，尝试使用587端口
   - 或者使用其他SMTP服务（如SMTP2GO）

2. **邮件投递问题**
   - 这是测试SMTP，不是生产邮件服务器
   - 外部邮件服务器可能会拒收来自IP的邮件
   - 适合测试防火墙设备，不建议用于正式业务

3. **安全性**
   - 当前配置为测试环境，未启用认证加密
   - 生产环境应使用TLS加密和SASL认证
   - 建议配置SPF、DKIM、DMARC等反垃圾邮件机制

---

## 🆘 故障排除

### 问题1：连接被拒绝

```bash
# 检查Postfix是否运行
sudo systemctl status postfix

# 检查端口监听
sudo netstat -tulpn | grep :25

# 检查防火墙
sudo ufw status
```

### 问题2：邮件发送失败

```bash
# 查看详细日志
sudo tail -100 /var/log/mail.log

# 测试本地投递
echo "test" | mail -s "test" root@localhost
```

### 问题3：权限错误

```bash
# 修复邮箱目录权限
sudo chown -R smtpuser:smtpuser /home/smtpuser/Maildir
sudo chmod -R 700 /home/smtpuser/Maildir
```

---

## 📞 其他选择

如果Postfix无法满足需求，可以使用以下替代方案：

1. **SMTP2GO** (推荐)
   - 免费：每月1000封邮件
   - 配置简单，无需授权码
   - 注册：https://www.smtp2go.com/

2. **SendGrid**
   - 免费：每天100封邮件
   - 大厂服务，稳定可靠
   - 注册：https://sendgrid.com/

3. **阿里云邮件推送**
   - 免费：每天200封
   - 国内速度快
   - HTTP API方式，无需SMTP

---

配置完成后，就可以在防火墙设备上测试邮件发送功能了！🎉
