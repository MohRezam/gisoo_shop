# from datetime import datetime
# import logging
# from typing import List
#
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
#
# from utils.general.logger import Logger
#
# logger = logging.getLogger("custom")
#
#
# class ElasticHelper:
#     def __init__(self, url, username, password, maxsize=10, verify_certs=False):
#         self.url = url
#         self.username = username
#         self.password = password
#         self.maxsize = maxsize
#         self.verify_certs = verify_certs
#         self.es = self.get_elasticsearch()
#
#     @staticmethod
#     def get_time_for_elastic(dt: "datetime"):
#         """
#         Get time for elastic
#         """
#         return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
#
#     def get_elasticsearch(self, maxsize=None):
#         if maxsize is None:
#             maxsize = self.maxsize
#         elasticsearch = Elasticsearch(
#             self.url,
#             http_auth=(self.username, self.password),
#             maxsize=maxsize,
#             verify_certs=self.verify_certs,
#         )
#         if elasticsearch is None:
#             raise ValueError("error in get elasticsearch")
#         return elasticsearch
#
#     def delete_elastic_data(self, index, query):
#         """
#         Delete elastic data
#         """
#         try:
#             result = self.es.delete_by_query(index=index, body={"query": query})
#             deleted_items = result.get("deleted")
#             if deleted_items is not None:
#                 Logger.info(
#                     logger,
#                     f"delete {deleted_items} document from elastic server index {index}",
#                     title="elasticsearch",
#                 )
#                 return deleted_items
#         except Exception as e:
#             Logger.error(
#                 logger,
#                 f"error in deleting elastic data for index {index}. error: {e}",
#                 title="elasticsearch",
#             )
#         return None
#
#     def delete_all_elastic_data(self, index):
#         """
#         Delete all elastic data
#         """
#         self.delete_elastic_data(index, query={"match_all": {}})
#
#     def create_index(self, index):
#         try:
#             self.es.create(index)
#             Logger.info(
#                 logger, f"index {index} created successfully", title="elasticsearch"
#             )
#             return True
#         except Exception as e:
#             Logger.error(
#                 logger,
#                 f"error in create index {index}, error: {e}",
#                 title="elasticsearch",
#             )
#             return False
#
#     def send_elastic(self, index, data_list: List[dict], chunk_size=200) -> bool:
#         """
#         Send data to elastic
#         """
#         try:
#             if not self.es.indices.exists(index=index):
#                 Logger.error(
#                     logger, f"not exists index {index}.", title="elasticsearch"
#                 )
#                 return False
#             success, failed = bulk(
#                 self.es,
#                 data_list,
#                 index=index,
#                 stats_only=True,
#                 raise_on_error=False,
#                 chunk_size=chunk_size,
#             )
#             Logger.info(
#                 logger,
#                 f"sending to index {index} is complete. "
#                 f"success: {success}, failed: {failed}",
#                 title="elasticsearch",
#             )
#             return True
#         except Exception as e:
#             Logger.error(
#                 logger,
#                 f"failed in sending to index {index}. Error: {e}",
#                 title="elasticsearch",
#             )
#             return False
