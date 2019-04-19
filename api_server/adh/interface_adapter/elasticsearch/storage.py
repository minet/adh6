from elasticsearch import Elasticsearch

from CONFIGURATION import ELK_HOSTS
from adh.constants import CTX_TESTING
from adh.use_case.interface.logs_repository import LogsRepository, LogFetchError
from adh.util.mac import get_mac_variations


class ElasticSearchStorage(LogsRepository):
    def get_logs(self, ctx, username=None, devices=None, limit=100):
        if not ELK_HOSTS:
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
                    "should": [  # "should" in a "bool" query basically act as a "OR"
                        {"match": {"message": username}},  # Match every log mentioning this member
                        # rules to match MACs addresses are added in the next chunk of code
                    ],
                    "minimum_should_match": 1,
                },
            },
            "_source": ["@   timestamp", "message"],  # discard any other field than timestamp & message
            "size": limit,
        }

        # Add the macs to the "should"
        for addr in devices:
            variations = map(
                lambda x: {"match_phrase": {"message": x}},
                get_mac_variations(addr)
            )
            query["query"]["bool"]["should"] += list(variations)

        # TODO(insolentbacon): instantiate only once the Elasticsearch client
        es = Elasticsearch(ELK_HOSTS)
        res = es.search(index="", body=query)['hits']['hits']

        return list(map(
            lambda x: "{} {}".format(x["_source"]["@timestamp"], x["_source"]["message"]),
            res
        ))