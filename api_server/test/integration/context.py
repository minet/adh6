# coding=utf-8
import sys

sys._called_from_test = True  # This will make sure we don't call 'init' anywhere else.

import common

app, _ = common.init(testing=True)

app.app.config["TESTING"] = True

from datetime import datetime, timedelta

tomorrow = datetime.now().date() + timedelta(1)
