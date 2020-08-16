# coding=utf-8
"""
Logs repository.
"""


import re

from elasticsearch import Elasticsearch

from src.constants import CTX_TESTING, LOG_DEFAULT_LIMIT

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

    def get_logs(self, ctx, limit=LOG_DEFAULT_LIMIT, username=None, devices=None, dhcp=False):
        """
        Get the logs related to the username and to the devices.
        :param ctx:  context
        :param username:  username
        :param devices:  MAC addresses of the devices
        :param limit: limit result
        :param dhcp: allow to query DHCP logs or not
        :return: logs
        """
        if not self.config.ELK_HOSTS:
            raise LogFetchError('no elk host configured')

        if ctx.get(CTX_TESTING):  # Do not actually query elasticsearch if testing...
            return ["test_log"]

        # Prepare the elasticsearch query...
        if not dhcp:
            query = {
                "sort": {
                    '@timestamp': 'desc',  # Sort by time
                },
                "query": {
                    "bool": {
                        "filter": {
                            "match": {"program": "radiusd"}
                        },
                        "should": [  # "should" in a "bool" query basically act as a "OR"
                            {"match": {"radius_user": username}},  # Match every log mentioning this member
                            # rules to match MACs addresses are added in the next chunk of code
                        ],
                        "minimum_should_match": 1,
                    },
                },
                "_source": ["@timestamp", "message", "src_mac"],  # discard any other field than timestamp & message
                "size": limit,
                "from": 0,
            }
        else:
            query = {
                "sort": {
                    '@timestamp': 'desc',  # Sort by time
                },
                "query": {
                    "constant_score": {
                        "filter": {
                            "bool": {
                                "should": [],
                                "minimum_should_match": 1,
                            },
                        },
                    },
                },
                "_source": ["@timestamp", "message", "program", "src_mac"],
                # discard any other field than timestamp & message
                "size": limit,
                "from": 0,
            }

        LOG.info(devices)
        # Add the macs to the "should"
        for d in devices:
            addr = d.mac
            variations = map(
                lambda x: {"match_phrase": {"src_mac": x}},
                get_mac_variations(addr)
            )

            if not dhcp:
                # noinspection PyTypeChecker
                query["query"]["bool"]["should"] += list(variations)
            else:
                # noinspection PyTypeChecker
                query["query"]["constant_score"]["filter"]["bool"]["should"] += list(variations)

        LOG.info('About to query ElasticSearch')
        res = self.es.search(index="", body=query)['hits']['hits']

        LOG.info(res)

        if not dhcp:
            for r in res:
                msg = re.sub('(?<=incorrect) \(.*(failed|incorrect)\)', '', r["_source"]["message"])
                msg = re.sub('\(from client .* (cli |tunnel)', '', msg)
                msg = re.sub('\) ', '', msg)
                msg = re.sub(' {0}P', ' P', msg)
                r["_source"]["message"] = msg

        return list(map(
            lambda x: "{} {}".format(x["_source"]["@timestamp"], x["_source"]["message"]),
            res
        ))
