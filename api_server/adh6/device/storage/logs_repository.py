# coding=utf-8
"""
Logs repository.
"""


from typing import List
import dateutil.parser
from elasticsearch import Elasticsearch

from adh6.constants import LOG_DEFAULT_LIMIT
from adh6.entity import Device, Member

from adh6.misc import get_mac_variations

from ..interfaces.logs_repository import LogsRepository


class ElasticsearchLogsRepository(LogsRepository):
    """
    Interface to the log repository.
    """

    def __init__(self):
        from flask import current_app
        self.config = current_app.config

        if 'ELK_HOSTS' not in self.config:
            return

        self.es = Elasticsearch(self.config['ELK_HOSTS'], http_auth=(self.config['ELK_USER'], self.config['ELK_SECRET']))

    def get(self, member: Member, devices: List[Device] = [], limit: int = LOG_DEFAULT_LIMIT, dhcp: bool = False):
        """
        Get the logs related to the username and to the devices.
        :param ctx:  context
        :param username:  username
        :param devices:  MAC addresses of the devices
        :param limit: limit result
        :param dhcp: allow to query DHCP logs or not
        :return: logs
        """
        if 'ELK_HOSTS' not in self.config:
            return [[1, "test_log"]]

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
                            {"match": {"radius_user": member.username}},  # Match every log mentioning this member
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

        res = self.es.search(index="", body=query)['hits']['hits']

        if not dhcp:
            for r in res:
                #msg = re.sub('(?<=incorrect) \(.*(failed|incorrect)\)', '', r["_source"]["message"])
                #msg = re.sub('\(from client .* (cli |tunnel)', '', r["_source"]["message"])
                #msg = re.sub('\) ', '', msg)
                #msg = re.sub(' {0}P', ' P', msg)
                #r["_source"]["message"] = r["_source"]["message"]
                pass

        return list(map(
            lambda x: [dateutil.parser.parse(x["_source"]["@timestamp"]), x["_source"]["message"]],
            res
        ))
