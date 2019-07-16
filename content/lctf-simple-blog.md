Title: LCTF2:a simple blog
Category: CTF
Date: 2017-11-21
slug: lctf-simple-blog

这个完全没思路，刚刚开始以为是mongo注入。看完write up才发现是N个知识点。

###敏感文件探索

<https://www.cdxy.me/?p=757>
<https://github.com/ring04h/weakfilescan.git>

平常扫描器是扫不到目录下的两个文件:`.login.php.swp, .admin.php.swp`

时候测试了下，首先使用猪猪侠的工具可以扫到`admin.php login.php`，其次是用cdxy写的工具，根据admin.php去扫，就可以得到敏感文件。

文件的恢复: `vim -r [swp]   :w [newfile]`


题目之前还是先纪录下padding oracle和CBC翻转攻击的原理。

####异或操作

<https://www.rawidn.com/posts/CBC-Byte-Flipping-Attack.html>

```
a, b = 10, 15
c = a ^ b
a = c ^ b
b = a ^ c

#这三个数可以互相转换

a = 10
a ^ a = 0
# 异或自己等于0

a = 10
a ^ 0 = 10
# 和0异或等于自身
```

加密过程:

![](https://ohduknodm.qnssl.com/20170525149569300467639.jpg)

解密过程:

![](https://ohduknodm.qnssl.com/20170525149569301911892.jpg)

* Plaintext: 待加密的数据
* IV: 随机加密的初始字符串（对于CBC类型的加密方式来说，每次需要一个input，这个input是固定的，但是最开始分组是没有input，这个IV就是座位input来输入的，为了保证密码的敏感性，雪崩效应）
<http://www.freebuf.com/articles/web/15504.html>
* Key: 加密的密钥
* Ciphertext: 加密后的数据
* CBC(Cipher Block Chaining)模式

> 在CBC模式中，首先将明文分组与前一个密文分组进行XOR运算，然后再进行加密，当加密第一个明文分组时，由于不存在“前一个密文分组”，因此需要事先准备一个长度为一个分组的比特序列来代替“前一个密文分组”，这个比特序列称为初始化向量（Initialization vector),通常缩写为IV,如果每次都使用相同的初始化向量（IV），当用同一密钥对同一明文进行加密时，所得到的密码一定是相同的，所以每次加密时都会随机产生一个不同的比特序列来作为初始化向量，避免这种情况产生。

Padding Oracle Attack攻击的原理是针对CBC链接模式的攻击，和具体的加密算法没有关系。


一般经过CBC模式加密之后的密文经常出现不可打印字符，为了保证网络上传输正确而不受系统间编码方案的影响，需要对密文进行“可视化”转化（即转化为可打印字符）。除了“ASCII十六进制表示方法”还可以采用base64编码，下面的login.php使用的是base64编码。




```
login.php:

function get_random_token(){
    $random_token = '';
    $str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
    for($i = 0; $i < 16; $i++){
        $random_token .= substr($str, rand(1, 61), 1);
    }
    return $random_token;
}

function get_identity(){
	global $id;
    $token = get_random_token();
    $c = openssl_encrypt($id, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $token);
    $_SESSION['id'] = base64_encode($c);
    setcookie("token", base64_encode($token));
    if($id === 'admin'){
    	$_SESSION['isadmin'] = 1;
    }else{
    	$_SESSION['isadmin'] = 0;
    }
}

function test_identity(){
    if (isset($_SESSION['id'])) {
        $c = base64_decode($_SESSION['id']);
        $token = base64_decode($_COOKIE["token"]);
        if($u = openssl_decrypt($c, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $token)){
            if ($u === 'admin') {
                $_SESSION['isadmin'] = 1;
                return 1;
            }
        }else{
            die("Error!");
        } 
    }
    return 0;
}

if(isset($_POST['username'])&&isset($_POST['password'])){
	$username = mysql_real_escape_string($_POST['username']);
	$password = $_POST['password'];
	$result = mysql_query("select password from users where username='" . $username . "'", $con);
	$row = mysql_fetch_array($result);
	if($row['password'] === md5($password)){
  		get_identity();
  		header('location: ./admin.php');
  	}else{
  		die('Login failed.');
  	}
}else{
	if(test_identity()){
        header('location: ./admin.php');
	}else{
        show_page();
    }
}
?>
```