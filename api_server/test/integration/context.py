# coding=utf-8
import common
import os

os.environ["ENVIRONMENT"] = "testing"
os.environ["TOKENINFO_FUNC"] = "test.auth.token_info"

app = common.init()

from datetime import datetime, timedelta

tomorrow = datetime.now().date() + timedelta(1)
