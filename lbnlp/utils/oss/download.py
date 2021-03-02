# -*- coding:utf-8 -*-
import os
import oss2


def download_model_from_oss(oss_conf, model_key, save_dir):
    # check for skip oss download
    save_path = os.path.join("/tmp", os.path.basename(model_key))
    if os.path.exists(save_path):
        return

    auth = oss2.Auth(oss_conf.access_key_id, oss_conf.access_key_secret)
    bucket = oss2.Bucket(auth, oss_conf.endpoint, oss_conf.bucket.strip("oss://"))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    bucket.get_object_to_file(model_key, save_path)
    os.system("tar zxf {} -C {}".format(save_path, save_dir))
