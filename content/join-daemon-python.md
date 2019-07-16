Title: setDaemon、join和threading
Category: Python
slug: setdaemon-join-threading
Date: 2017-12-14

<http://www.cnblogs.com/nwf5d/archive/2011/11/20/2256376.html>

Python中的thread一些机制和C/C++不同，在C/C++中，主线程结束后，其子线程会默认被主线程kill掉。而在python中，主线程结束后，会默认等待子线程结束后，主线程才退出。

python对于thread的管理中有两个函数: join和setDaemon

>join
如果一个线程B中调用thread.join()，则thread结束后，线程B才会接着thread.join()往后运行

所以这样一个例子:

```
import threading
import time

class my(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)


	def run(self):
		global n, lock
		time.sleep(1)
		if lock.acquire():
			print n, self.name
			n += 1
			lock.release()


if "__main__" == __name__:
	n = 1
	Threadlist = []
	lock = threading.Lock()
	for i in range(1, 1000):
		t = my()
		Threadlist.append(t)
	for t in Threadlist:
		# t.daemon = True
		t.start()
	for t in Threadlist:
		t.join()
```

上面的脚本会一瞬间完成，如果把:

```
for t in Threadlist:
    t.join


这个for注释掉，变成:

for t in Threadlist:
    t.start()
    t.join()
```
这样运行结果就是跟单线程一样，因为`t.join()`会导致下一个线程阻塞，只有当前join的线程完成之后，才会下一个运行。

>Wait until the thread terminates. This blocks the calling thread until the thread whose join() method is called terminates – either normally or through an unhandled exception – or until the optional timeout occurs.