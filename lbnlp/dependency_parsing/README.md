## Performance
> MacBook Pro 18款 <br>
> Mem: 700Mi <br>
> Average Cost Time:<br>
> 1. 2952字，55个句子，30s
> 2. 1947字，29个句子，10s

## CONLL格式释义
1    ID      当前词在句子中的序号，１开始.<br>
2    FORM    当前词语或标点<br>
3    LEMMA   当前词语（或标点）的原型或词干，在中文中，此列与FORM相同<br>
4    UPOS    当前词语的通用词性标签<br>
5    XPOS    当前词语的特定语言的词性标签<br>
6    FEATS   句法特征，在本次评测中，此列未被使用，全部以下划线代替。<br>
7    HEAD    当前词语的中心词<br>
8    DEPS    当前词语与中心词的依存关系<br>
9    MISC    其它备注<br>
参考：https://universaldependencies.org/format.html

## 依存关系符号释义
符号|释义|...
---|:--:|--:
nn| 复合名词修饰|
punct| 标点符号|
nsubj| 名词性主语|
conj| 连接性状语|
dobj| 直接宾语|
advmod| 名词性状语|
prep| 介词性修饰语|
nummod| 数词修饰语|
amod| 形容词修饰语|
pobj| 介词性宾语|
rcmod| 相关关系|
cpm| 补语|
assm| 关联标记|
assmod| 关联修饰|
cc| 并列关系|
elf| 类别修饰|
ccomp| 从句补充|
det| 限定语|
lobj| 时间介词|
range| 数量词间接宾语|
asp| 时态标记|
tmod| 时间修饰语|
plmod| 介词性地点修饰|
attr| 属性|
mmod| 情态动词|
loc| 位置补语|
top| 主题|
pccomp| 介词补语|
etc| 省略关系|
lccomp| 位置补语|
ordmod| 量词修饰|
xsubj| 控制主语|
neg| 否定修饰|
rcomp| 结果补语|
comod| 并列联合动词|
vmod| 动词修饰|
prtmod| 小品词|
ba| 把字关系|
dvpm| 地字修饰|
dvpmod| 地字动词短语|
prnmod| 插入词修饰|
cop| 系动词|
pass| 被动标记|
nsubjpass| 被动名词主语|
clf| 类别修饰|
dep| 依赖关系|
root| 核心关系