#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import logging
import os
import requests as _requests
import requests.exceptions as _requests_exceptions

_store_all_host = os.environ["STORE_SERVICE_ALL_HOST"]
_store_all_port = int(os.environ.get("STORE_SERVICE_ALL_PORT", 8080))
_store_all_url = f"http://{_store_all_host}:{_store_all_port}"

_factory_all_host = os.environ["FACTORY_SERVICE_ALL_HOST"]
_factory_all_port = int(os.environ.get("FACTORY_SERVICE_ALL_PORT", 8080))
_factory_all_url = f"http://{_factory_all_host}:{_factory_all_port}"

_factory_any_host = os.environ["FACTORY_SERVICE_ANY_HOST"]
_factory_any_port = int(os.environ.get("FACTORY_SERVICE_ANY_PORT", 8080))
_factory_any_url = f"http://{_factory_any_host}:{_factory_any_port}"

_log = logging.getLogger("client")

class Client:
    def get_json(self, url, **params):
        _log.info(f"Calling {url} (GET)")

        response = _requests.get(url)

        try:
            response.raise_for_status()
        except _requests_exceptions.HTTPError as e:
            _log.exception(e)
            raise

        response_data = response.json()

        _log.info(f"Response data: {response_data}")

        return response_data

    def post_json(self, url, request_data):
        _log.info(f"Calling {url} (POST)")
        _log.info(f"Request data: {request_data}")

        response = _requests.post(url, json=request_data)

        try:
            response.raise_for_status()
        except _requests_exceptions.HTTPError as e:
            _log.exception(e)
            raise

        response_data = response.json()

        _log.info(f"Response data: {response_data}")

        return response_data

    def check_errors(self, data):
        for response in data:
            error = response["content"]["error"]

            if error is not None:
                _log.warning(f"Error in aggregated response: {error}")

    def find_items_url(self, product=None, size=None, color=None):
        return f"{_store_all_url}/api/find-items"

    def find_items(self, product=None, size=None, color=None):
        url = self.find_items_url(product, size, color)
        data = _requests.get(url).json()

        # Special case for testing
        if isinstance(data, dict):
            data = [{"content": data}]

        self.check_errors(data)

        results = list()

        for response in data:
            results.extend(response["content"]["results"])

        return results

    def find_orders_url(self, product=None, size=None, color=None):
        return f"{_factory_all_url}/api/find-orders"

    def find_orders(self, product=None, size=None, color=None):
        url = self.find_orders_url(product, size, color)
        data = _requests.get(url).json()

        # Special case for testing
        if isinstance(data, dict):
            data = [{"content": data}]

        self.check_errors(data)

        results = list()

        for response in data:
            results.extend(response["content"]["results"])

        return results

    def order_item(self, order):
        url = f"{_factory_any_url}/api/order-item"

        request_data = {
            "order": order.data(),
        }

        response_data = self.post_json(url, request_data)

        return request_data, response_data

    def stock_item(self, item):
        host = os.environ.get("STORE_SERVICE_STORE_ID_OVERRIDE", item.store.id)
        port = int(os.environ.get("STORE_SERVICE_PORT", 8080))
        url = f"http://{host}:{port}/api/stock-item"

        request_data = {
            "item": item.data(),
        }

        response_data = self.post_json(url, request_data)

        return request_data, response_data
