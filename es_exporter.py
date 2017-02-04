import time
import datetime
import logging
import json
import arrow
import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from urllib3 import Timeout

LOGSTASH_INDEX_PREFIX = 'filebeat'
URL = "http://localhost:9200/%s-%s.%s.%s/_search"
SERVER_PORT = 8000

# ES queries
# LAST_FIELD_QUERY = {"query": {"match_all": {}}, "size": 1, "sort": [{"%s": {"order": "desc"}}]}
#SEARCH_STRUCTURE = {"query": {"match": {"%s": "%s"}}}
SEARCH_TERM_RANGE = '{"query": {\
    "bool": {"must": {"match": {"%s": "%s"}}, "filter": {"range": {"@timestamp": {"gte": "%s", "lt": "%s"}}}}}}'


class ESCollector(object):
    def __init__(self, config, lst=0):
        self.config = config
        self.last_scrape_timestamp = lst

    def collect(self):
        metric = GaugeMetricFamily(
            self.config["name"],
            self.config["help"],
            labels=['login'])

        occurences = {}  # aux dict to store name and value

        # execute if not first scrape
        if self.last_scrape_timestamp != 0:

            for (item, values) in self.config["fields"].items():
                response = make_request_to_es(SEARCH_TERM_RANGE % (
                    values["field"], values["match"], arrow.get(self.last_scrape_timestamp),
                    arrow.get(arrow.utcnow().timestamp)))
                if response is not None:
                    occurences[item] = response["hits"]["total"]

        else:  # if first run set values to 0
            logging.debug("First run of collector, set occurences to 0")
            for (item, values) in self.config["fields"].items():
                occurences[item] = 0.0

        # Add result to metric
        for (key, value) in occurences.items():
            labellist = [key]
            logging.debug("Add metric %s value %d to prometheus" % (key, value))
            metric.add_metric(labellist, float(value))

        logging.debug("Last scrape timestamp set to %s" % self.last_scrape_timestamp)

        # store timestamp for the next scrape
        self.last_scrape_timestamp = arrow.utcnow()
        # return result
        yield metric


'''
Make a request to Elastisearch
'''


def make_request_to_es(query):
    pass
    now = datetime.datetime.now()
    url = (URL % (LOGSTASH_INDEX_PREFIX, now.year, ("%02d" % now.month), ("%02d" % now.day)))

    try:
        r = requests.get(url, data=query)
    except requests.exceptions.RequestException:
        logging.debug("Request to %s error." % url)
        return

    return r.json()


'''
Parse ES timestamp from a ES respose and return it in long format
'''


def get_timestamp_from_request(result, item_number=0):
    if result["hits"]["total"] > 0:
        ts_aux = result["hits"]["hits"][item_number]["_source"]["@timestamp"]

    ar = arrow.get(ts_aux)
    return ar.timestamp


def load_configuration():
    with open('./config.json', 'r') as f:
        config = json.load(f)
        logging.info("Configuration loaded.")
    return config


def main(last_scrape_timestamp=0):
    # if last_scrape_timestamp == 0:  # if first time scrape
    #     # get last timestamp
    #     result = make_request_to_es((json.dumps(LAST_FIELD_QUERY) % "@timestamp"))
    #
    #     print(json.dumps(result))
    #
    #     last_scrape_timestamp = get_timestamp_from_request(result)

    logging.basicConfig(level=logging.DEBUG)
    config = load_configuration()

    collector = ESCollector(config)
    REGISTRY.register(collector)
    start_http_server(SERVER_PORT)
    logging.info("ES exporter started listening on port %s " % SERVER_PORT)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()