Title: 简单的python HTTP服务器
Category: Python
Date: 2017-5-19
slug: python-http


```
# coding: utf-8
import socket
import sys
import datetime


host = '0.0.0.0'    # 本机地址
port = int(sys.argv[1])          # 监听端口
data_payload = 65535     # 一次接受数据大小上限
backlog = 15             # 限制最大连接数量

def echo_server(port):
    # 创建socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 开启端口重用
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定socket到端口
    server_address = (host,port)
    print "Starting up echo server on %s:%s" % server_address
    sock.bind(server_address)
    # 限制最大连接数量
    sock.listen(backlog)
    # 监听循环
    i = 0
    while True:
        print "[%s]: %s: %s" % (i, datetime.datetime.now(), "Waiting==============")
        client, address = sock.accept()
        data = client.recv(data_payload)
        if data:
            print "Received data: %s" % data
            # 回显
            client.send(data)
            i += 1
            #print "Data have sent back!"
        # 关闭链接
        client.close()

if __name__ == '__main__':
    # 启动服务器
    echo_server(port)
```

