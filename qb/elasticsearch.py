from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import NotFoundError


def get_es_connection(hosts=['192.168.99.100']):
	try:
		return connections.create_connection(hosts=hosts)
	except NotFoundError:
		return []