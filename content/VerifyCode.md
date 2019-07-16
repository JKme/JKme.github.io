Title: 验证码识别
Date: 2017-9-26
Category: Learning
slug: verifyCode


先灰度处理

```
img = Image.open('1317.png') # 打开图片
img = img.convert('L') # 转换成灰度图片
img.save('1317-L.png') # 保存图片
```
然后是二值化, 二值化处理之后，投影

以预发布为例子，获取验证的url: https://wxxx.net/api/h5/getVerifyCode
得到的验证码是base64编码，使用python解码之后保存即可:

```
import requests
url = "https://xxxxx/getVerifyCode"

for i in range(20):
	imgfile = str(i) + '.jpg'
	req = requests.get(url)
	image_data = req.json()["result"]["imageEncode"]
	fh = open("/xxx/Desktop/imagecode/" + imgfile, "wb")
	fh.write(image_data.decode('base64'))
```

上面的代码可以获取20个验证码，
然后处理验证码：

先灰度处理--> 二值化 --> 投影或者使用8邻域算法

我们这里使用8邻域算法。

```
# coding: utf-8
from PIL import Image
import os
import re
import pytesseract

def binarizing(img, threshold):
   img = img.convert("L")
   pixdata = img.load()
   w, h = img.size
   for y in range(h):
      for x in range(w):
         if pixdata[x, y] < threshold:
            pixdata[x, y] = 0
         else:
            pixdata[x, y] = 255
   return img
   # img.save("/xxx/Desktop/imagecode/43.jpg")


def depoint(img):
   pixdata = img.load()
   w,h = img.size
   for y in range(1,h-1):
      for x in range(1, w-1):
         count = 0
         if pixdata[x, y-1] > 245:
            count = count + 1
         if pixdata[x, y+1] > 245:
            count = count + 1
         if pixdata[x-1, y] > 245:
            count = count + 1
         if pixdata[x+1, y] > 245:
            count = count + 1
         if pixdata[x-1, y-1] > 245:
            count = count + 1
         if pixdata[x-1, y+1] > 245:
            count = count + 1
         if pixdata[x+1, y-1] > 245:
            count = count + 1
         if pixdata[x+1, y+1] > 245:
            count = count + 1
         if count > 4:
            pixdata[x, y] = 255
   return img

path = "/xxx/Desktop/imagecode"
pattern = re.compile(r"[a-zA-Z0-9]")
images = os.listdir(path)
for image in images:
   if image.split(".")[1] == "jpg":
      img = Image.open("/xxx/Desktop/imagecode/" + image)
      b_img = binarizing(img, 230)
      v = depoint(b_img)
      vcode = pytesseract.image_to_string(v)
      matches = re.findall(pattern, vcode)
      filename = ''.join(map(str, matches))
      v.save("/xxx/Desktop/train/" + filename + '.jpg')
```


<http://www.hi-roy.com/source/all-tags/%E9%AA%8C%E8%AF%81%E7%A0%81%E8%AF%86%E5%88%AB/>