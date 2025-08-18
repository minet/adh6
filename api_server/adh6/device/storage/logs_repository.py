"""
Logs repository.
"""

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

        if "ELK_HOSTS" not in self.config:
            return

        self.es = Elasticsearch(
            self.config["ELK_HOSTS"], http_auth=(self.config["ELK_USER"], self.config["ELK_SECRET"])
        )

    def get(
        self,
        member: Member,
        devices: list[Device] = [],
        limit: int = LOG_DEFAULT_LIMIT,
        offset: int = 0,
        dhcp: bool = False,
    ):
        """
        Get the logs related to the username and to the devices.
        :param member: Member object
        :param devices: MAC addresses of the devices
        :param limit: limit result
        :param offset: offset for pagination
        :param dhcp: allow to query DHCP logs or not
        :return: tuple of (logs, total_count)
        """
        if "ELK_HOSTS" not in self.config:
            # Mock data for development
            # Generate a large number of mock logs to test pagination
            mock_logs = [
                [dateutil.parser.parse(f"2024-01-{(i % 31) + 1:02d}T10:{(i % 60):02d}:00Z"), f"test_log_{i}"]
                for i in range(1, 1001)
            ]
            paginated_logs = mock_logs[offset : offset + limit]
            return paginated_logs, len(mock_logs)

        # First, get the total count
        count_query = {
            "query": {
                "bool": {
                    "filter": {"match": {"program": "radiusd"}},
                    "should": [
                        {"match": {"radius_user": member.username}},
                    ],
                    "minimum_should_match": 1,
                },
            },
        }

        if dhcp:
            count_query = {
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
            }

        # Add the macs to the count query
        for d in devices:
            addr = d.mac
            variations = ({"match_phrase": {"src_mac": x}} for x in get_mac_variations(addr))

            if not dhcp:
                count_query["query"]["bool"]["should"] += list(variations)
            else:
                count_query["query"]["constant_score"]["filter"]["bool"]["should"] += list(variations)

        # Get total count
        total_count = self.es.count(index="", body=count_query)["count"]

        # Prepare the elasticsearch query for actual logs...
        if not dhcp:
            query = {
                "sort": {
                    "@timestamp": "desc",  # Sort by time
                },
                "query": {
                    "bool": {
                        "filter": {"match": {"program": "radiusd"}},
                        "should": [  # "should" in a "bool" query basically act as a "OR"
                            {"match": {"radius_user": member.username}},  # Match every log mentioning this member
                            # rules to match MACs addresses are added in the next chunk of code
                        ],
                        "minimum_should_match": 1,
                    },
                },
                "_source": ["@timestamp", "message", "src_mac"],  # discard any other field than timestamp & message
                "size": limit,
                "from": offset,
            }
        else:
            query = {
                "sort": {
                    "@timestamp": "desc",  # Sort by time
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
                "from": offset,
            }

        # Add the macs to the "should"
        for d in devices:
            addr = d.mac
            variations = ({"match_phrase": {"src_mac": x}} for x in get_mac_variations(addr))

            if not dhcp:
                # noinspection PyTypeChecker
                query["query"]["bool"]["should"] += list(variations)
            else:
                # noinspection PyTypeChecker
                query["query"]["constant_score"]["filter"]["bool"]["should"] += list(variations)

        res = self.es.search(index="", body=query)["hits"]["hits"]

        if not dhcp:
            for r in res:
                # msg = re.sub('(?<=incorrect) \(.*(failed|incorrect)\)', '', r["_source"]["message"])
                # msg = re.sub('\(from client .* (cli |tunnel)', '', r["_source"]["message"])
                # msg = re.sub('\) ', '', msg)
                # msg = re.sub(' {0}P', ' P', msg)
                # r["_source"]["message"] = r["_source"]["message"]
                pass

        logs = [[dateutil.parser.parse(x["_source"]["@timestamp"]), x["_source"]["message"]] for x in res]
        return logs, total_count
