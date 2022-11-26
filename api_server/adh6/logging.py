import logging

def setup_login():
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(threadName)s - %(module)s : %(funcName)s - %(message)s','%Y-%m-%dT%H:%M:%SZ')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)