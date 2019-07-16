Title: Linux复制带动态库的命令
Date: 2017-3-9
slug: copy-linux-share-lib
Category:Pentest


需求： 从一台Linux复制命令到另外一台上面，由于命令依赖动态库，比如gcc:

```
ldd `which gcc`
	linux-vdso.so.1 =>  (0x00007fffdb7eb000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fcf12441000)
	/lib64/ld-linux-x86-64.so.2 (0x000055a28350c000)
```

这种情况下单单复制gcc没卵用，google了下找到某个bash脚本:

```
#!/bin/bash

if [ $# != 2 ] ; then
    echo "usage $0 PATH_TO_BINARY TARGET_FOLDER"
    exit 1
fi

PATH_TO_BINARY="$1"
TARGET_FOLDER="$2"

# if we cannot find the the binary we have to abort
if [ ! -f "$PATH_TO_BINARY" ] ; then
    echo "The file '$PATH_TO_BINARY' was not found. Aborting!"
    exit 1
fi

# copy the binary to the target folder
# create directories if required
echo "---> copy binary itself"
cp --parents -v "$PATH_TO_BINARY" "$TARGET_FOLDER"

# copy the required shared libs to the target folder
# create directories if required
echo "---> copy libraries"
for lib in `ldd "$PATH_TO_BINARY" | cut -d'>' -f2 | awk '{print $1}'` ; do
   if [ -f "$lib" ] ; then
        cp -v --parents "$lib" "$TARGET_FOLDER"
   fi  
done

# I'm on a 64bit system at home. the following code will be not required on a 32bit system.
# however, I've not tested that yet
# create lib64 - if required and link the content from lib to it
if [ ! -d "$TARGET_FOLDER/lib64" ] ; then
    mkdir -v "$TARGET_FOLDER/lib64"
fi
```

用法: `exportbin.sh <path to the binary>  <target floder>`


* http://www.metashock.de/2012/11/export-binary-with-lib-dependencies/