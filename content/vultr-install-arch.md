Title: vultr安装Arch
Date: 2016-10-11
Category: Fun
slug: vultr-arch-install

```
分两个区：grub和其他
gdisk /dev/vda   
n
回车
回车
+2M #bios 分区大小
EF02 #分区系统文件
#下面是格式化，直接使用剩下的分区
mkfs.ext4 /dev/vda2
mount /dev/vda2 /mnt 
pacstrap /mnt base base-devel net-tools
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt /bin/bash 

#安装引导
pacman -S grub
pacman -S openssh #安装ssh
grub-install --target=i386-pc /dev/vda
grub-mkconfig -o /boot/grub/grub.cfg
systemctl enable dhcpcd #自动分配IP
systemctl enable sshd   #开机启动ssh

如果开机没网络不通，需要手动添加ip,加多少看自己的面板
ifconfig ens3 up
ip addr add 1.1.1.1/255.255.254.0 broadcast 255.255.254.0 dev ens3
ip route add default via 2.2.2.2
安装好之后的系统是不允许ssh，root远程访问
可以添加新用户：
useradd -m -G wheel -s /bin/bash some
或者修改/etc/ssh/sshd_config 添加
PermitRootLogin yes

最后添加aur源
[archlinuxcn]
SigLevel = Optional TrustedOnly
Server = https://cdn.repo.archlinuxcn.org/$arch

[archlinuxfr]
Server = http://repo.archlinux.fr/$arch
```


====
更新


分区可以这样分:

```
parted /dev/sda
(parted) mklabel msdos
(parted) mkpart primary ext4 1M 120M
(parted) set 1 boot on
(parted) mkpart primary ext4 120M 10G
(parted) mkpart primary linux-swap 10G 12G
(parted) mkpart primary ext4 12G 100%

说明:

/boot 1-120M 用于挂在/boot分区设置为bootable
/     120M-10G挂载 / 分区
swap  10G-12G 用于交换分区
/home 12G-100%  剩余空间挂载home分区

# 打印分区信息
# p 

# 退出(quit)
# q 



```

分区之后格式化:

```
# mkfs.ext4 /dev/sda1
# mkfs.ext4 /dev/sda2
# mkfs.ext4 /dev/sda4
# mkswap /dev/sda3
```

挂载分区:

```
# mount /dev/sda2 /mnt
# mkdir /mnt/{boot,home}
# mount /dev/sda1 /mnt/boot
# mount /dev/sda4 /mnt/home
# swapon /dev/sda3
```