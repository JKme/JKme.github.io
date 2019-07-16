Title: openResty的waf尝试
Category: Learning
Date: 2017-11-8
slug: openresty-waf


```
* set_by_lua: 流程分支处理判断变量初始化
* rewrite_by_lua: 转发，重定向，缓存等功能
* access_by_lua: IP准入，接口权限等情况集中处理
* content_by_lua： 内容生成
* body_filter_by_lua: 应答body过滤处理
* Header_filter_by_lua: 应答HTTP过滤处理
* log_by_lua: 回话完成后本地异步完成日志记录
```  

local logger = require "resty.logger.socket"

计划：以x.x.x.x作为测试目标，使用openresty反代到另外一个端口

不用修改nginx的日志格式，修改lua脚本。

openwaf如何获取日志的／
或者最简单的 这个logger的用法


```

-- lua_package_path "/path/to/lua-resty-logger-socket/lib/?.lua;;";
--
--    server {
--        location / {
--            content_by_lua_file lua/log.lua;
--        }
--    }

-- lua/log.lua
local logger = require "resty.logger.socket"
if not logger.initted() then
    local ok, err = logger.init{
        host = 'xxx',
        port = 1234,
        flush_limit = 1,   --日志长度大于flush_limit的时候会将msg信息推送一次
        drop_limit = 99999,
    }
    if not ok then
        ngx.log(ngx.ERR, "failed to initialize the logger: ",err)
        return
    end
end

local msg = string.format(.....)
local bytes, err = logger.log(msg)
if err then
    ngx.log(ngx.ERR, "failed to log message: ", err)
    return
end
```