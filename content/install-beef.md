Title: Beef安装
Date: 2016-8-30
Category: Learning
slug: beef-install


##Beef安装:

先安装rvm:

```
gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
\curl -sSL https://get.rvm.io | bash -s stable

```
然后切换到git clone下来的beef目录，貌似会自动提示安装2.3.0，

```
rvm install ruby-2.3.0
gem install bundler
bundle install 

Done
```

先安装ruby，如果VPS多个版本ruby并且是ubuntu的时候，使用

```
update-alternatives --install /usr/local/bin/gem gem /usr/local/ruby/bin/gem 1111 //新增gem
update-alternatives --config gem //切换gem版本
```
记录下bundle的一个坑坑坑坑坑，艹草草草草草：


VPS上面安装的bundle在安装的时候总是找gem1.8，明明我都装好了，他还找1.8，并且已经设置好了gem和ruby，最后我ls了一下ruby的安装目录里面有一个活生生的bundle，最后用绝对路径就安装好了。

`/usr/local/ruby/bin/bundle install `


```
git clone https://github.com/beefproject/beef.git
cd beef
gem install bundler
bundle install
./beef  //启动
```
##与Metasploit关联

```
./beef/config.yaml
		metasploit:
			enable: true
./beef/extensions/demos/config/yaml
		enable: true
./beef/extensions/metasploit/config.yaml
		ssl: true
		ssl_version: 'TLSv1'


//一般安装beef之后会升级ruby，所以需要进入msf安装目录运行下
gem install bundler
bundle install
//启动msf
msfconsole
load msgrpc ServerHost=127.0.0.1 User=msf Pass=abc123 SSL=y

//然后再运行beff 
./beef

```
