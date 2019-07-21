Title:tmux使用
Date: 2019-06-24
Slug: tmux
Category: Learning

组合键:

:new<回车>  启动新会话
s           列出所有会话
w           相当于s的时候展开列表，展开windows
$           重命名当前会话


tmux kill-session -t demo # 关闭demo会话

他有一个session,windows,panes的概念

一个session可以有N个windows，N个panes

如果是最大化利用，那么需要找到一种可以跳来跳去的方法，不管是跳windows还是session。

一般来说是跳windows，因为windows下有几个不同的panes

所以，怎么跳最快?

name不管是pane还是windows，是不是只要有name就可以跳过去，不对，应该是windows之间的跳，因为一组windows就是一组任务。

一个session里面可以最下面的状态栏可以看到有几个windows，windows的名字如何

###windows的操作:
```
p  切换到上一个windows
n  切换到下一个widnwos
,  重命名窗口
.  修改当前窗口编号
f  根据关键词搜索windows   这个实际测试可用，可以跳session
```


###Pane的操作

```
{  向前置换面板
}  向后置换面板，这个有意思
z  最大化当前的面板，再输入一次就变回去了
Esc+1  横着的面板变成竖立状态
```

###Pane和windows之间的互换
比如你当前想把另外一个windows合并到现在的pane里面

```
join-pane -s window01 # 合并名称为window01的窗口的默认（第一个）面板到当前窗口中
join-pane -s window01.1 # .1显式指定了第一个面板，.2就是第二个面板(我本地将面板编号起始值设置为1，默认是0)
```

有另外一种方式，通过karabiner，单独在iterm2里面绑定某个组合键盘，比如cap绑定一个Home键，这样tmux的prefix就是单独按一下cap就可以了。

所以需要两个地方设置:

```
set -g prefix Home
unbind C-b
bind-key Home send-prefix
```
第二个地方需要在karabiner里面针对iterm2单独设置一个规则: 即按下cap等于home键。
这个是网上的一个例子，可以照着写

```
?xml version="1.0"?>
<root>
  <appdef>
    <appname>PYCHARM</appname>
    <equal>com.jetbrains.pycharm</equal>
  </appdef>
   <item>
    <name>custom settings</name>
    <item>
      <name>Change Functional Keys to F3...F10 for PyCharm</name>
      <identifier>remap.app_pycharm_functional2function</identifier>
      <only>PYCHARM</only>
      <autogen>__KeyToKey__ KeyCode::EXPOSE_ALL, KeyCode::F3</autogen>
      <autogen>__KeyToKey__ KeyCode::DASHBOARD, KeyCode::F4</autogen>
      <autogen>__KeyToKey__ KeyCode::LAUNCHPAD, KeyCode::F4</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::KEYBOARDLIGHT_LOW, KeyCode::F5</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::KEYBOARDLIGHT_HIGH, KeyCode::F6</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::MUSIC_PREV, KeyCode::F7</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::MUSIC_PLAY, KeyCode::F8</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::MUSIC_NEXT, KeyCode::F9</autogen>
      <autogen>__KeyToKey__ ConsumerKeyCode::VOLUME_MUTE, KeyCode::F10</autogen>
    </item>
  </item>
</root>
```

获取程序的`budnle identifiers`:

```  
> osascript -e 'id of app "WebStorm"'
  com.jetbrains.WebStorm

  > osascript -e 'id of app "Pycharm"'
  com.jetbrains.pycharm
```

tmux的最大化利用是远程服务器的时候，在iterm2里面新开一个标签。可以选择每一个vps一个标签，然后在每一个标签里面利用tmux,w

可以在iterm2里面修改切换tab是`cmd + [`，和`cmd + ]`。


```

#(date)	shell command
#I	window index
#S	session name
#W	window name
#F	window flags
#H	Hostname
#h	Hostname, short
#D	pane id
#P	pane index
#T	pane title
```
最后，我的tmux配置是这个:

```
unbind C-b
set -g prefix C-d

bind r source-file ~/.tmux.conf \; display-message "Config reloaded"


set -g default-terminal "screen-256color"
set -g mode-keys vi
run-shell "tmux rename-window \"#{pane_current_command}\""


bind \ split-window -h
bind - split-window -v

bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R
bind q killp

set -g base-index 1
setw -g pane-base-index 1
set-option -g status-interval 1


#set-option -g automatic-rename on
#set-option -g automatic-rename-format '#{b:pane_current_path}'

set-window-option -g window-status-current-format '#[fg=white,bold]** #{window_index} #[fg=green]#W #[fg=blue]#(echo "#{pane_current_path}" | rev | cut -d'/' -f-3 | rev) #[fg=white]**|'
set-window-option -g window-status-format '#[fg=white,bold]#{window_index} #[fg=green]#W #[fg=blue]#(echo "#{pane_current_path}" | rev | cut -d'/' -f-3 | rev) #[fg=white]|'
bind-key -r w choose-window -F '#{window_index} | #{pane_current_command} | #{pane_current_path}'
#bind-key -r w choose-window -F '#{window_index} | #{pane_current_command} | #{host} | #{pane_current_path}'

# status bar updates every 15s by default**, change to 1s here
# (this step is optional - a lower latency might have negative battery/cpu usage impacts)
setw -g mouse on
#set -g mouse-select-pane on
#set -g mouse-resize-pane on
#set -g mouse-select-window on

set -g status-fg white
set -g status-bg black
setw -g window-status-fg cyan
setw -g window-status-bg default
setw -g window-status-attr dim

setw -g window-status-current-fg white
setw -g window-status-current-bg red
setw -g window-status-current-attr bright
set -g pane-border-fg green
set -g pane-border-bg black
set -g pane-active-border-fg red
set -g pane-active-border-bg black
bind-key -t vi-copy Enter copy-pipe "nc localhost 8377"

set -g status-left-length 40
#set -g status-left "#[fg=green]Session[#S] #[fg=yellow]#I #[fg=cyan]#P"
set -g status-left "#[fg=green][#S]"
set-option -g set-titles on
set-option -g set-titles-string '#h:#S.#I.#P #W #T' # window number,program name, active(or not)

set -g history-limit 10000

set -g status-right "#[fg=cyan] #(date '+%%Y-%%B')"
#set -g status-right "#[fg-cyan] %Y-%m"
#set -g status-right '#[fg=green,bg=default,bright]#(uptime) #[fg=white,bg=default]%l:%M:%S %p#[default] #[fg=blue]%Y-%m-%d%a'
setw -g monitor-activity on
setw -g bell-action any
set -g visual-activity on
set -g status-justify centre
bind-key J command-prompt -p "Create pane from window #:" "join-pane -s ':%%'"
set-option -s set-clipboard off


set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'

# plugins
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-save-interval '0'
set -g @continuum-restore 'on'
set -g @plugin 'tmux-plugins/tmux-yank'
run-shell ~/.tmux/plugins/tmux-resurrect/resurrect.tmux
r

run '~/.tmux/plugins/tpm/tpm'

```

再安装一个tpm插件:

```
mkdir -p ~/.tmux/plugins/
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

Press prefix + I (capital i, as in Install) to fetch the plugin.
```


`I`安装插件，

saved a session (prefix + ctrl-s) 

最后的最后，如果是本机macosx，远程是vps，当复制远程vps内容的时候，复制的内容是到了远程主机的buffer，这个时候需要clipper来把远程主机复制到本地，我用的tmux版本是2.1。在mac上的ssh配置文件加上端口转发:

```
RemoteForward 8377 localhost:8377
```

配置开机启动:

```
sudo cp clipper /usr/local/bin
cp contrib/darwin/tcp-port/com.wincent.clipper.plist ~/Library/LaunchAgents/
launchctl load -w -S Aqua ~/Library/LaunchAgents/com.wincent.clipper.plist
```

然后在远程主机的tmux配置加上这样:

```
bind-key -t vi-copy Enter copy-pipe "nc localhost 8377"

```
这样就可以了。

在使用mosh的情况下，mosh是不支持端口转发的，需要先用ssh端口转发，然后再用mosh链接:

```
Host sandbox
  ControlMaster no
  ControlPath none
  Hostname sandbox.example.com

Host sandbox-clipper
  ControlMaster no
  ControlPath none
  ExitOnForwardFailure yes
  Hostname sandbox.example.com
  RemoteForward 8377 localhost:8377
  
ssh -N -f sandbox-clipper
mosh sandbox
```

clipper的文档讲的超级详细，可以看看。

<https://github.com/wincent/clipper>
