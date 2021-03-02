# coding: utf8

import os
import json
import hanlp
import time
import traceback
from collections import namedtuple
from lbnlp.utils.oss import OssConfig
from lbnlp.utils.oss import download_model_from_oss


# model path
MTL_MODEL_KEY = "algo-models/dependency_parsing/mtl/close_tok_pos_ner_srl_dep_sdp_con_electra_small_20210111_124159.tar.gz"
SAVE_DIR = "$AIRFLOW_HOME/var/models/dependency_parsing/mtl"


class DependencyParsing:
    """
    """
    def __init__(self, oss_conf: namedtuple):
        self.mlt = None
        self.load_model(oss_conf)

    def load_model(self, oss_conf: namedtuple):
        download_model_from_oss(oss_conf, MTL_MODEL_KEY, SAVE_DIR)
        model_dir = os.path.join(SAVE_DIR, os.path.basename(MTL_MODEL_KEY).strip(".tar.gz"))
        self.mlt = hanlp.load(model_dir)

    @staticmethod
    def get_sentences(text):
        # 空格替换换行符
        texts = text.split("\\n")
        ret = []
        for text in texts:
            if text.strip() == "":
                continue
            # 去掉连续的空格
            items = text.split()
            new_text = ""
            for item in items:
                if new_text == "":
                    new_text = item
                elif u'\u4e00' <= new_text[-1] <= u'\u9fa5' or u'\u4e00' <= item[0] <= u'\u9fa5':
                    new_text += item
                else:
                    new_text += " " + item
            sentences = [sent for sent in hanlp.utils.rules.split_sentence(new_text)]
            ret.extend(sentences)
        return ret

    def predict(self, text):
        # 单文本预测
        sentences = self.get_sentences(text)
        ok = False
        sentence_structure = None
        words_count = 0
        valid_rel_count = 0
        nsubjs_count = 0
        dobjs_count = 0
        preview_text = ""
        phrase_max_depth_lst = []
        doc = self.mlt(sentences)
        conll_lst = doc.to_conll()
        con_lst = doc["con"]
        for i in range(len(sentences)):
            pr = ParsingResult(i, conll_lst[i], con_lst[i])


            ss = pr.main_part()
            if not ok:
                if i == 0:
                    sentence_structure = ss
                if ss.primary_root != "" and len(ss.primary_nsubjs) != 0 and len(ss.primary_dobjs) != 0:
                    sentence_structure = ss
                    ok = True
            words_count += count_valid_words(doc["tok/fine"][i])
            valid_phrase_cnt, phrase_max_depth = pr.valid_phrase_info()
            phrase_max_depth_lst.append(phrase_max_depth)
            valid_rel_count += valid_phrase_cnt
            nsubjs_count += pr.nsubjs_count()
            dobjs_count += pr.nobjs_count()
            preview_text += ss.preview_text + "\n" + "-" * 80 + "\n"
        ret = DependencyParsingResult(
            sentence_structure=sentence_structure,
            features_deep=round(sum(phrase_max_depth_lst) * 1.0 / len(sentences), 4),
            words_count=words_count,
            sentences_count=len(sentences),
            features_count=valid_rel_count,
            parameters=Parameters(nsubjs_count, dobjs_count),
            preview_text=preview_text
        )
        return ret


def count_valid_words(words):
    """统计有效词语数量，不包括空白符和标点符号。
    """
    count = 0
    for word in words:
        if word.isalnum() or is_contain_chinese(word):
            count += 1
    return count


def is_contain_chinese(s):
    for c in s:
        if u'\u4e00' <= c <= u'\u9fff':
            return True
    return False


SentenceStructure = namedtuple(
    "SentenceStructure",
    ["index", "sentence", "primary_root", "primary_nsubjs", "primary_dobjs", "preview_text"]
)

DependencyParsingResult = namedtuple(
    "DependencyParsingResult",
    [
        "sentence_structure",
        "features_deep",
        "words_count",
        "sentences_count",
        "features_count",
        "parameters",
        "preview_text"
    ]
)

Parameters = namedtuple(
    "Parameters",
    ["nsubjs_count", "dobjs_count"]
)

# 主语类型
SUBJECTS = set([
    "nsubj",  # 名词性主语
    "top",
])
# 宾语类型
OBJECTS = set([
    "dobj",  # 直接宾语
    "attr",
    "nsubjpass",  # 被动名词主语
])
# 中心词
CENTRAL_WORDS = set(["root"])
# 有效类型
VALID_REL = set([
    "assmod",  # 关联修饰
    "prep",  # 介词修饰语
    "root",  # 根节点
    "nsubj",  # 名词主语
    "dep",  # 依赖关系
    "nn",  # 名词组合形式
    "advmod",  # 副词修饰
    "dobj",  # 直接宾语
    "case",  # 格标记
    "conj",  # 连词
])
# 特定短语结构
VALID_CON = [
    ["NP", "NDP", "NP"],
    ["VP", "VV", "VP"],
    ["VP", "ADVP", "VP"],
    ["IP", "NP", "VP", "PU"],
    ["VP", "VV", "NP"],
    ["PP", "P", "NP"],
    ["NP", "NN", "NN"],
    ["DNP", "NP", "DEG"],
    ["IP", "VP", "PU"],
    ["IP", "NP", "VP"],
    ["CP", "IP", "DEC"]
]


class ParsingResult:
    """
    """

    def __init__(self, index, coll, con):
        self.index = index
        self.coll = coll
        self.con = con
        self.sentence = self.get_sentence()
        self.fas = [[] for _ in range(len(coll))]

    def get_sentence(self):
        sentence = ""
        for tok in self.coll:
            sentence += tok["form"]
        return sentence

    def main_part(self):
        """主干部分
        :return:
        """
        preview_text = str(self.coll)
        try:
            preview_text = self.coll.to_tree()
        except Exception as _:
            traceback.print_exc()
        preview_text = preview_text.replace("'", "’")

        root_idx = self.get_root_idx()
        if root_idx <= 0:
            return SentenceStructure(
                index=self.index,
                sentence=self.sentence,
                primary_nsubjs=[],
                primary_root=self.get_np_phrase(),
                primary_dobjs=[],
                preview_text=preview_text,
            )
        if self.coll[root_idx - 1]["upos"] == "NP":
            return SentenceStructure(
                index=self.index,
                sentence=self.sentence,
                primary_nsubjs=[],
                primary_root=self.get_np_phrase(),
                primary_dobjs=[],
                preview_text=preview_text
            )

        root_word = self.coll[root_idx - 1]["form"]

        primary_nsubjs = []
        primary_dobjs = []
        primary_root = root_word

        for tok in self.coll:
            if tok["head"] != root_idx:
                continue
            if tok["deprel"] in SUBJECTS:
                nn_phrase = self.combine_nn(tok["id"])
                primary_nsubjs.append(nn_phrase)
            if tok["deprel"] in OBJECTS:
                nn_phrase = self.combine_nn(tok["id"])
                primary_dobjs.append(nn_phrase)
            if len(primary_nsubjs) != 0 and len(primary_dobjs) != 0:
                break

        return SentenceStructure(
            index=self.index,
            sentence=self.sentence,
            primary_nsubjs=primary_nsubjs,
            primary_root=primary_root,
            primary_dobjs=primary_dobjs,
            preview_text=preview_text,
        )

    def get_np_phrase(self):
        """主干部分是名词性短语
        :return:
        """
        phrase_list = []
        for tok in self.coll:
            if self.is_pre_pre_terminal(tok["id"]) and tok["upos"] == "NP":
                phrase = ""
                for leaf in self.get_leaves(tok["id"], set()):
                    phrase += self.coll[leaf - 1]["form"]
                phrase_list.append(phrase)
        return "\\".join(phrase_list)

    def is_pre_pre_terminal(self, target):
        leaves = self.get_leaves(target, set())
        if len(leaves) == 1 and target == leaves[0]:
            return False
        ok = True
        for leaf in leaves:
            fa = self.coll[leaf - 1]["head"]
            if fa == 0:
                ok = False
                break
            grand_fa = self.coll[fa - 1]["head"]
            if grand_fa != target:
                ok = False
                break
        return ok

    def get_leaves(self, target, walked=set()):
        walked.add(target)
        leaves = []
        for tok in self.coll:
            if tok["head"] == target and tok["id"] not in walked:
                leaves.extend(self.get_leaves(tok["id"], walked))
        if len(leaves) == 0:
            leaves = [target]
        return leaves

    def combine_nn(self, target):
        # 合并名词性短语为一个节点
        if target is None or target <= 0:
            return ""
        phrase = self.coll[target - 1]["form"]
        for tok in self.coll:
            if tok["head"] == target and tok["deprel"] == "nn":
                phrase = tok["form"] + phrase
                break
        return phrase

    def get_root_idx(self):
        for tok in self.coll:
            if tok["deprel"] in CENTRAL_WORDS:
                return tok["id"]
        return 0

    def valid_phrase_info(self):
        """有效短语结构计数以及最大深度
        :return:
        """
        def is_valid(tree):
            if not isinstance(tree, list):
                return False
            for special_struct in VALID_CON:
                if tree.label() == special_struct[0]:
                    children = set([child.label() for child in tree])
                    if children == set(special_struct[1:]):
                        return True
            return False

        def find_valid_struct(tree):
            if not isinstance(tree, list):
                return False
            ret = 1 if is_valid(tree) else 0
            for child in tree:
                ret += find_valid_struct(child)
            return ret

        def walk_for_max_depth(tree):
            if not isinstance(tree, list):
                return 0
            if is_valid(tree):
                return tree.height()
            ret = 0
            for child in tree:
                ret = max(ret, walk_for_max_depth(child))
            return ret

        return find_valid_struct(self.con), walk_for_max_depth(self.con)

    def nsubjs_count(self):
        return sum([1 if tok["deprel"] == "nsubj" else 0 for tok in self.coll])

    def nobjs_count(self):
        return sum([1 if tok["deprel"] == "dobj" else 0 for tok in self.coll])


if __name__ == "__main__":
    with open("test.txt") as f:
        test_text = f.read()

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

    t = time.time()

    result = dependency_parsing.predict(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(result.preview_text)

    print("cost: {}ms".format((time.time() - t) * 1000))
