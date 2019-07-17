Title: GitPages搭建Pelican博客
Date: 2016-3-29
Category: Python
slug: gitpages-pelican

参考:<https://pages.github.com/>
##0x00
在Github创建一个`username.github.io`的代码仓库，以我的为例子，先创建`JKme.github.io`
##0x01
克隆到本机，使用virtualenv来做一个隔离的环境：

`git clone https://github.com/JKme/JKme.github.io.git`


本机安装virtualenv：

`pip install virtualenv`

把`export PIP_REQUIRE_VIRTUALENV=true`，添加到`~/.zshrc`或者`~/.bashrc`

初始化virtualenv：

```bash
cd JKme.github.io
mkdir env
virtualenv env
source ~/.zshrc
source env/bin/activate
echo env/ >> .gitignore //忽略virtualenv环境变量
```

##0x02
新建一个分支，在这个分支上面操作content里面的内容和pelican配置文件：

`git checkout -b source`

安装pelican和Markdown，并开始pelican配置过程：

```bash
pip install pelican Markdown
pelican-quickstart
```
##0x03
现在测试一下可以写first.md：

```
Title: Hello
Date: 2016-3-29

Do the right thing,
Do the right thing.
```
然后可以输出html：`make html`
##0x04
上传到github，使用gh-pages

```
pip install ghp-import
git branch gh-pages
ghp-import output
git checkout master
git merge gh-pages
git push --all
```

##Tips
如果再次写文章需要先切换到source，总的来说是这么个顺序：

```shell
#!/bin/bash
DATE=`date +%Y-%m-%d:%H:%M:%S`
cd /home/someone/code/JKme.github.io
source env/bin/active
git checkout source
make html
git add .
git commit -m $DATE
ghp-import output
git checkout master
git merge gh-pages --no-commit
git commit -m $DATE	
git push --all
```
先切换到source，初始化虚拟环境，然后再编辑文章，如果本来系统安装了pelican，而没有初始化虚拟环境，那么可能会发生其他不可预期的后果。以上脚本也可以这样子，修改当前source分支下的`Makefile`文件，在github选项里面，注释掉原来的内容，前面变量添加上一句DATE=`date +%Y-%m-%d:%H:%M:%S`（我使用这个date是用时间来区分每次commit的信息），然后再在github添加以下的内容:

```bash

github: publish
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) && git add . && git commit -m $DATE && ghp-import output
	git checkout master && git merge gh-pages --no-commit && git commit -m $DATE && git push --all
	
```

这样子写完文章之后直接在source的分支下`make github`即可推送到GitPages。







