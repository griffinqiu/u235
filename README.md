# u235
### Long Bridge Natural Language Processing (LB-NLP)
####  Install
```bash
$ pip install lbnlp@git+ssh://git@github.com/griffinqiu/u235.git
```
#### Set Environment Variables (Canary)
```bash
$ export oss_access_key_id=xxxx
$ export oss_access_key_secret=xxxx
$ export oss_bucket=xxxx
$ export oss_endpoint=xxxx
```
#### Dependency Parsing Demo
```python
import os
import json
from lbnlp.utils import OssConfig
from lbnlp.dependency_parsing import DependencyParsing

test_text = "2 月 24 日周一，追随隔夜欧亚股指的跌势，美股三大指数大幅跳空低开，盘初道指 30 个成分股和标普 11 大板块全线下跌，科技和芯片股领跌大盘。"

oss_access_key_id = os.getenv("oss_access_key_id")
oss_access_key_secret = os.getenv("oss_access_key_secret")
oss_bucket = os.getenv("oss_bucket")
oss_endpoint = os.getenv("oss_endpoint")
oss_conf = OssConfig(
    oss_access_key_id,
    oss_access_key_secret,
    oss_bucket,
    oss_endpoint
)

dependency_parsing = DependencyParsing(oss_conf)
result = dependency_parsing.predict(test_text)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(result.preview_text)
```
#### Topic Predict Demo
```python
import os
from lbnlp.utils import OssConfig
from lbnlp.topic_clustering import TopicCluster
text = "智通财经 APP 讯，苏大维格 (300331.SZ) 公告，公司近日收到中华国际科学交流基金会发出的《关于第四届杰出工程师奖推荐人选获奖的通知》(中科金 [2020] 029 号)，公司董事长陈林森荣获第四届 “杰出工程师奖”。公司称，本次 “杰出工程师奖” 的获得，是对公司及董事长陈林森个人在微纳光学制造领域技术研究与产品开发实力的高度认可。"

oss_access_key_id = os.getenv("oss_access_key_id")
oss_access_key_secret = os.getenv("oss_access_key_secret")
oss_bucket = os.getenv("oss_bucket")
oss_endpoint = os.getenv("oss_endpoint")
oss_conf = OssConfig(
    oss_access_key_id,
    oss_access_key_secret,
    oss_bucket,
    oss_endpoint
)

topic_cluster = TopicCluster(oss_conf)
result = topic_cluster.predict([text])

print(result)
```
