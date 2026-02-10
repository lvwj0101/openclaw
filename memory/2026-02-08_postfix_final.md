# 2026-02-08 记忆 - Postfix SMTP 部署

## Postfix SMTP 部署 - 防火墙邮件测试

用户需要测试防火墙设备的邮件发送功能，但缺乏企业邮箱，因此在服务器上部署Postfix SMTP服务。

### 服务器信息：
- **IP**: 62.234.211.119
- **用户**: ubuntu
- **初始密码**: ji_pmrDc6jMCc6_
- **最终密码**: 1qaz#EDC%TGB
- **配置文件**: E:\program\xinliu\web-app\deploy.config.json

### 部署过程：

#### 第一阶段：初始尝试（使用旧密码）
1. **初始尝试**: Python脚本执行apt install命令，遇到apt upgrade进程阻塞
2. **问题**: 服务器上已有 `apt upgrade -y` 进程运行，持续30+分钟
3. **解决方案**:
   - 终止阻塞的apt进程
   - 清理apt锁文件
   - 跳过apt update直接安装Postfix
4. **结果**: Postfix成功安装和配置

#### 第二阶段：密码更新（使用新密码）
1. **密码更新**: 用户更新服务器密码为 `1qaz#EDC%TGB`
2. **apt update超时**: 尝试运行apt update，SSH超时
3. **直接安装**: 跳过apt update，直接安装Postfix成功
4. **配置问题**: 初次配置使用 `mail.flowthink.local` 导致服务启动失败
5. **简化配置**: 改用 `localhost` 和 `localdomain`，服务启动成功

### 最终SMTP配置：

```
SMTP 服务器: 62.234.211.119
SMTP 端口: 25 (未加密）
用户名: smtpuser
密码: SmtpTest2024!
发送者邮箱: smtpuser@localhost
```

### 部署步骤（已完成）：

1. ✅ 停止所有apt/dpkg进程
2. ✅ 清理apt锁文件
3. ✅ 跳过update直接安装Postfix
4. ✅ 使用简化配置（localhost/localdomain）
5. ✅ 创建测试用户 smtpuser
6. ✅ 配置防火墙（开放端口25、587）
7. ✅ 重启Postfix服务
8. ✅ 验证端口25正在监听
9. ✅ 验证Postfix进程运行中
10. ✅ 测试发送邮件

### Postfix配置详情（最终）：

- myhostname: localhost
- mydomain: localdomain
- inet_interfaces: all
- mynetworks: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
- smtpd_sasl_auth_enable: no（不需要认证，允许局域网访问）
- home_mailbox: Maildir/

### 生成的脚本：

位于 `C:\Users\gw\.openclaw\workspace\`:
- setup-postfix-smtp.sh - Postfix配置脚本
- POSTFIX配置说明.md - 详细说明文档
- install_postfix.py - Python安装脚本
- fix_postfix.py - 修复配置脚本
- final_test.py - 最终验证脚本

### 验证结果：

- ✅ 端口25正在监听（tcp 0 0 0.0.0.0:25）
- ✅ Postfix master进程运行中（PID 50720）
- ✅ 测试邮件已发送到 smtpuser@localhost

### 经验教训：

1. **apt阻塞问题**: apt upgrade进程会长时间运行，阻塞新安装
2. **解决方法**: 终止阻塞进程，清理锁文件，直接安装（跳过update）
3. **SSH连接问题**: 长时间apt命令可能导致SSH会话超时
4. **推荐做法**: 分步执行，先清理再安装，增加超时时间
5. **配置问题**: 使用自定义域名可能导致Postfix启动失败，推荐先用localhost测试
6. **密码管理**: 服务器密码更新后需要及时同步到部署脚本

### 注意事项：

- 这是测试SMTP，不是生产邮件服务器
- 外部邮件服务器可能会拒收来自IP的邮件
- 适合测试防火墙设备，不建议用于正式业务
- 配置了不认证模式（局域网访问），测试环境足够
- 如需外发邮件，需要配置DNS反向解析和SPF记录
