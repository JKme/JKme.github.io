Title: lctf-1萌萌哒报名系统writeup
Category: CTF
slug: lctf-1
Date: 2017-11-20


第一次参加CTF，虽然我知道自己很菜。。可是没想到这么菜。

前面的题目没头脑，只有这个开始有点思路。

```
天依花了一整天的时间用IDE开发了一个报名系统，现在她睡着了，难道你们不想做点什么嘛XD?http://123.206.120.239/
```
按照尿性我先开了目录扫描过一遍果然没东西，然后肯定是跟IDE有关系，我就去自己的phpstorm项目的目录下喵了眼，果然存在.idea文件夹。进去之后可以在`/.idea/workspace.xml`文件里面找到一个压缩包。（这里我进去之后就没细看，直接google去看看能不能根据这个文件反推出来源代码去了，经过提醒才看到2333）

然后就是下载源代码分析:

login.php

```
<?php
	session_start();
	include('config.php');
	try{
		$pdo = new PDO('mysql:host=localhost;dbname=xdcms', $user, $pass);
	}catch (Exception $e){
		die('mysql connected error');
	}
	$username = (isset($_POST['username']) === true && $_POST['username'] !== '') ? (string)$_POST['username'] : die('Missing username');
    $password = (isset($_POST['password']) === true && $_POST['password'] !== '') ? (string)$_POST['password'] : die('Missing password');

    if (strlen($username) > 32 || strlen($password) > 32) {
        die('Invalid input');
    }

    $sth = $pdo->prepare('SELECT password FROM users WHERE username = :username');
    $sth->execute([':username' => $username]);
    if ($sth->fetch()[0] !== $password) {
        die('wrong password');
    }
    $_SESSION['username'] = $username;
	unset($_SESSION['is_logined']);
	unset($_SESSION['is_guest']);
	#echo $username;
	header("Location: member.php");
?>
```

register.php

```
<?php
	include('config.php');
	try{
		$pdo = new PDO('mysql:host=localhost;dbname=xdcms', $user, $pass);
	}catch (Exception $e){
		die('mysql connected error');
	}
	$admin = "xdsec"."###".str_shuffle('you_are_the_member_of_xdsec_here_is_your_flag');
    $username = (isset($_POST['username']) === true && $_POST['username'] !== '') ? (string)$_POST['username'] : die('Missing username');
    $password = (isset($_POST['password']) === true && $_POST['password'] !== '') ? (string)$_POST['password'] : die('Missing password');
    $code = (isset($_POST['code']) === true) ? (string)$_POST['code'] : '';

    if (strlen($username) > 16 || strlen($username) > 16) {
        die('Invalid input');
    }

    $sth = $pdo->prepare('SELECT username FROM users WHERE username = :username');
    $sth->execute([':username' => $username]);
    if ($sth->fetch() !== false) {
        die('username has been registered');
    }

    $sth = $pdo->prepare('INSERT INTO users (username, password) VALUES (:username, :password)');
    $sth->execute([':username' => $username, ':password' => $password]);

    preg_match('/^(xdsec)((?:###|\w)+)$/i', $code, $matches);
    if (count($matches) === 3 && $admin === $matches[0]) {
        $sth = $pdo->prepare('INSERT INTO identities (username, identity) VALUES (:username, :identity)');
        $sth->execute([':username' => $username, ':identity' => $matches[1]]);
    } else {
        $sth = $pdo->prepare('INSERT INTO identities (username, identity) VALUES (:username, "GUEST")');
        $sth->execute([':username' => $username]);
    }
	echo '<script>alert("register success");location.href="./index.html"</script>';
```

member.php:

```
<?php
	error_reporting(0);
	session_start();
	include('config.php');
	if (isset($_SESSION['username']) === false) {
        die('please login first');
    }
	try{
		$pdo = new PDO('mysql:host=localhost;dbname=xdcms', $user, $pass);
	}catch (Exception $e){
		die('mysql connected error');
	}
    $sth = $pdo->prepare('SELECT identity FROM identities WHERE username = :username');
    $sth->execute([':username' => $_SESSION['username']]);
    if ($sth->fetch()[0] === 'GUEST') {
        $_SESSION['is_guest'] = true;
    }

    $_SESSION['is_logined'] = true;
	if (isset($_SESSION['is_logined']) === false || isset($_SESSION['is_guest']) === true) {
        
    }else{
		if(isset($_GET['file'])===false)
			echo "None";
		elseif(is_file($_GET['file']))
			echo "you cannot give me a file";
		else
			readfile($_GET['file']);
	}
?>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body background="./images/1.jpg">
<object type="application/x-shockwave-flash" style="outline:none;" data="http://cdn.abowman.com/widgets/hamster/hamster.swf?" width="300" height="225"><param name="movie" value="http://cdn.abowman.com/widgets/hamster/hamster.swf?"></param><param name="AllowScriptAccess" value="always"></param><param name="wmode" value="opaque"></param></object>
<p style="color:orange">你好啊，但是你好像不是XDSEC的人,所以我就不给你flag啦~~</p>
</body>
</html>
```


这道题目有两种解法：

##预期解法preg_match

register.php的时候，有preg_match，在preg_match匹配子查询的时候，如果匹配的字符过多，会导致匹配失效，这个payload大概需要10w个字符串，导致php超时，这个时候脚本没有response，但是实际注册成功的。此时用户既不是guest，也不是xdsec。这样再次登录的时候，就绕过if的判断，进去读取文件的流程。

这里需要绕过is_file的判断，做题目的时候直接google下找到了`/config.php`这样可以绕过is_file函数，但是后面的readfile读取的时候会失败，所以脚本写错了，解是实用php://filter来读取文件。

```
php://filter/read=convert.base64-encode/resource=config.php
php://filter/read=string.toupper/resource=config.php

```

##条件竞争

>因为身份验证是用if ($sth->fetch()[0] === 'GUEST')那么如果在identities表中没有username这一行数据，那么取出来$sth->fetch()[0]结果就是null,还是可以绕过第一层，所以可以用python多线程注册用户，在

```
$sth = $pdo->prepare('INSERT INTO identities (username, identity) VALUES (:username, :identity)');
```
语句执行之前登陆上去就可以绕过第一层。

<https://github.com/LCTF/LCTF2017/tree/master/src/web/%E8%90%8C%E8%90%8C%E5%93%92%E7%9A%84%E6%8A%A5%E5%90%8D%E7%B3%BB%E7%BB%9F>