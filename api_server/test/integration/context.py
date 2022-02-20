# coding=utf-8
import common
import os

os.environ["ENVIRONMENT"] = "testing"

app = common.init()

from datetime import datetime, timedelta

tomorrow = datetime.now().date() + timedelta(1)
