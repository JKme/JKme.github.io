Title: Python处理数据到ELK
Category: Learn
slug: python-elk-date
Date: 2020-05-06


需要把数据从xlsx读到elk，再做数据分析，遇到一个问题是把当在elk里面处理日期类的数据的时候，需要把数据转换为Date类型:

```python
def float2utc(num):
	date = datetime.datetime(*xldate_as_tuple(num, 0))

	local = pytz.timezone("Asia/Shanghai")
	local_dt = local.localize(date, is_dst=None)
	utc_dt = local_dt.astimezone(pytz.utc)
	timeStr = datetime.datetime.strftime(utc_dt, "%Y-%m-%dT%H:%M:%S.%f")
	timeStr = timeStr[:-3]
	#cell = date.strftime('%Y/%m/%d %H:%M')
	return timeStr + "Z"

```


* <https://stackoverflow.com/questions/40294803/datetime-in-elasticsearch-how-to-handle-timezon>