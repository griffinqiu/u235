# coding: utf8

import os
import oss2
import jieba
import time
import numpy as np
from gensim import corpora
from gensim import models
from collections import namedtuple
from lbnlp.utils.oss import OssConfig
from lbnlp.utils.oss import download_model_from_oss


# model path
DICT_PATH = "algo-models/topic_clustering/lsi_below-5_above-0.15_topic-20/dict.json"
TFIDF_MODEL_PATH = "algo-models/topic_clustering/lsi_below-5_above-0.15_topic-20/tfidf.model"
LSI_MODEL_PATH = "algo-models/topic_clustering/lsi_below-5_above-0.15_topic-20/lsi.model"
MODEL_KEY = "algo-models/topic_clustering/lsi_below-5_above-0.15_topic-20.tar.gz"
SAVE_DIR = "/opt/algo-models/topic_clustering/"


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)


class TopicCluster:
    def __init__(self, oss_conf: namedtuple):
        self.dictionary = None
        self.tfidf_model = None
        self.lsi_model = None
        self.load_model(oss_conf)

    def load_model(self, oss_conf: namedtuple):
        download_model_from_oss(oss_conf, MODEL_KEY, SAVE_DIR)
        self.dictionary = corpora.Dictionary.load(os.path.join("/opt", DICT_PATH))
        self.tfidf_model = models.TfidfModel.load(os.path.join("/opt", TFIDF_MODEL_PATH))
        self.lsi_model = models.LsiModel.load(os.path.join("/opt", LSI_MODEL_PATH))

    def predict(self, docs: list):
        corpus = [jieba.cut_for_search(doc) for doc in docs]
        print(corpus)
        bow_corpus = [self.dictionary.doc2bow(doc) for doc in corpus]
        tfidf_corpus = [self.tfidf_model[doc] for doc in bow_corpus]
        lsi_corpus = [self.lsi_model[doc] for doc in tfidf_corpus]
        ret = []
        for lsi_vector in lsi_corpus:
            row = [v for _, v in lsi_vector]
            row = softmax(np.asarray(row))
            ret.append(row)
        return ret


if __name__ == "__main__":
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

    t = time.time()

    result = topic_cluster.predict([text] * 100)
    print(result)
    print("cost: {}".format((time.time() - t) * 10))
