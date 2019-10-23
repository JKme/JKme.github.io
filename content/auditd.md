Title: 利用auditd记录history
Category: Pentest
slug: auditd
Date: 2019-9-11

Centos系自带auditd，比如监控execve这些关键函数，再比如想记录用户的历史命令。

```
pam_tty_audit.so
```
修改`/etc/pam.d/sshd`，可以记录使用ssh登录的用户的历史记录，看上去么得卵用，因为最后的history都会保留在`/root/.bash_history`。But，他可以记录密码。比如登录到其他站点的密码。

```
session required pam_tty_audit.so disable=*  enable=root log_passwd
```

同理，可以把这一行加入到`/etc/pam.d/su`,`/etc/pamd.sudo`等文件里面，然后使用下面命令来查看，可以把他当作另类的键盘记录器。

```
/usr/sbin/aureport --tty
```

保存之后重启sshd的进程。