# coding=utf-8
"""
Logs repository.
"""

from elasticsearch import Elasticsearch

from src.constants import CTX_TESTING, DEFAULT_LIMIT
from src.use_case.interface.logs_repository import LogsRepository
from src.exceptions import LogFetchError
from src.util.mac import get_mac_variations
from src.util.log import LOG


class ElasticSearchRepository(LogsRepository):
    """
    Interface to the log repository.
    """

    def __init__(self, configuration):
        self.config = configuration
        LOG.info('About to instantiate ElasticSearch')
        LOG.debug('ELK_HOSTS:' + str(self.config.ELK_HOSTS))
        self.es = Elasticsearch(self.config.ELK_HOSTS)

    def get_logs(self, ctx, limit=DEFAULT_LIMIT, username=None, devices=None):
        """
        Get the logs related to the username and to the devices.
        :param ctx:  context
        :param username:  username
        :param devices:  MAC addresses of the devices
        :param limit: limit result
        :return: logs
        """
        if not self.config.ELK_HOSTS:
            raise LogFetchError('no elk host configured')

        if ctx.get(CTX_TESTING):  # Do not actually query elasticsearch if testing...
            return ["test_log"]

        # Prepare the elasticsearch query...
        query = {
            "sort": {
                '@timestamp': 'desc',  # Sort by time
            },
            "query": {
                "bool": {
                    "filter": {
                        "match": {"program": "radiusd"}
                    },
                    "must": {
                      "match": {"tags": "anonymous"}
                    },
                    "should": [  # "should" in a "bool" query basically act as a "OR"
                        {"match": {"radius_user": username}},  # Match every log mentioning this member
                        # rules to match MACs addresses are added in the next chunk of code
                    ],
                    "minimum_should_match": 1,
                },
            },
            "_source": ["@timestamp", "message"],  # discard any other field than timestamp & message
            "size": limit,
            "from": 0,
        }

        LOG.info(devices)
        # Add the macs to the "should"
        for d in devices:
            addr = d.mac_address
            variations = map(
                lambda x: {"match_phrase": {"message": x}},
                get_mac_variations(addr)
            )
            # noinspection PyTypeChecker
            query["query"]["bool"]["should"] += list(variations)

        LOG.info('About to query ElasticSearch')
        res = self.es.search(index="", body=query)['hits']['hits']

        return list(map(
            lambda x: "{} {}".format(x["_source"]["@timestamp"], x["_source"]["message"]),
            res
        ))
