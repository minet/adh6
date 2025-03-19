import os
from datetime import datetime, timedelta

import adh6.server as server

os.environ["ENVIRONMENT"] = "testing"
# os.environ["TOKENINFO_FUNC"] = "test.auth.token_info"

app = server.init()


tomorrow = datetime.now().date() + timedelta(1)
