from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import requests
import tornado
import os
import logging
import json

EXTENSION_URL = "/spark"

# Example usage: tornado_logger.error("This is an error!")
tornado_logger = logging.getLogger("tornado.application")

def raise_error(msg):
    raise tornado.web.HTTPError(500, "ERROR: " + msg)

class SparkHandler(IPythonHandler):
    def get(self):
        #tornado_logger.info("Received URI from client: " + self.request.uri)
        if not self.request.uri.startswith(EXTENSION_URL):
            raise_error("URI did not start with " + EXTENSION_URL)
        spark_request = "http://localhost:4040" + self.request.uri[len(EXTENSION_URL):]
        #tornado_logger.info("Sending request to Spark UI: " + spark_request)

        try:
            spark_response = requests.get(spark_request)
            client_response = spark_response.text
            #tornado_logger.info("Receiving response from Spark UI: " + client_response)
        except requests.exceptions.RequestException:
            client_response = json.dumps({"error": "SPARK_NOT_RUNNING"})
            #tornado_logger.info("No response received from Spark UI. Generating error response: " + client_response)

        self.write(client_response)
        self.flush()

def load_jupyter_server_extension(nb_server_app):
    web_app = nb_server_app.web_app
    host_pattern = ".*$"
    route_pattern = url_path_join(web_app.settings['base_url'], EXTENSION_URL) + ".*"
    web_app.add_handlers(host_pattern, [(route_pattern, SparkHandler)])