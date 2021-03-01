from collections import namedtuple
OssConfig = namedtuple(
    "OssConfig",
    ["access_key_id", "access_key_secret", "bucket", "endpoint"]
)
