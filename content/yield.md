Title: 协程
Category: Python
Date: 2017-12-20
Slug: python-concurrent

Python里面，当线程比较多的时候，线程的切换是一件十分耗时的工作，但是python里面提供了一个比较好玩的东西，协程来解决这个问题。
适合IO密集型的任务，协程运行在单个线程中，避免多线程模型的上下文切换，减少了很大开销，所以适合线程数比较大的程序。

svn的扫描是同步程序，所以最好的方式是实用异步socket＋协程。这样处理速度应该是最快的

await 和 async def区分生成器和协程

协程经历大概三个阶段：

1. 最初生成器变形yield/send
2. 引入@asyncio.coroutime和yield from
3. 在3.5版本引入async和await关键字


<http://www.cnblogs.com/linhaifeng/articles/7429894.html>
里面程序实现可以得出结果:

```
yield 单纯的切换会降低运行效率
yield 不能实现遇到IO就切换程序
```

所以会有后来的`get_event_loop()`来获取当前的IOevent么？使用event_loop卡住主线程？

完美状态就是在yield的时候，继续下一个任务的运行，等上一个任务完成之后，在yield之后继续运行。

```
1. 可以控制在多个任务之间切换，切换之前的状态保存下来，在重新运行的时候，基于暂停的位置继续执行
2. 作为1的补充，可以检测IO操作，在遇到io操作的情况下才发生切换。
```
yield from 是什么鬼：<http://blog.theerrorlog.com/yield-from-in-python-3.html>

所以如果threads比较多，在python3里面可以使用asyncio来降低上下文切换带来的性能损失。
asyncio的缺陷，如果使用它，那么所有的io api都要使用异步的版本。


当一个函数内部出现了yield语句时，它就不再是一个单纯的函数，而是一个生成器函数，调用它并不会执行它的代码，而是返回一个生成器。
调用这个生成器的send方法时，才回执行内部代码，当执行到yield时，这个send方法就返回了，调用者可以得到其返回值。send方法在第一次调用时，参数必须为None，python2可以使用它的next方法，python3里面改成了`__nexe__`方法，还可以使用内置的next函数调用。

send可以多次调用，参数作为yield的返回值，回到生成器上一次执行的地方，并继续执行下去。当生成器的代码执行完时，会抛出一个`StopIteration`的异常。python3.3开始可以在生成器使用return，返回值可以从`StopIteration`异常的value属性获取。

`for...in...`循环会自动捕获`StopIteration`异常，并作为循环停止的条件。

由此可见，yield是可以用作跳转的。而我们要做的就是在遇到IO请求时，用yield返回IO Loop；当事件发生时，找到对应的生成器，用send方法继续执行即可。









<https://www.secpulse.com/archives/61398.html>
<https://ayonel.me/index.php/2017/05/17/coroutine_spider/> 完整的代码实现
<http://kissg.me/2016/06/01/a-web-crawler-with-asyncio-coroutines> 翻译的
<https://www.zybuluo.com/chyoo1991/note/179220> yield和send的代码实现
<http://lucumr.pocoo.org/2016/10/30/i-dont-understand-asyncio/> 
<http://www.cnblogs.com/linhaifeng/articles/7429894.html>
<https://www.keakon.net/2017/06/28/%E7%94%A8Python3%E7%9A%84async/await%E5%81%9A%E5%BC%82%E6%AD%A5%E7%BC%96%E7%A8%8B>

https://lightless.me/archives/python-coroutine-from-boom-to-dead-to-rebirth.html