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

import binascii as _binascii
import threading as _threading
import uuid as _uuid

_log = logging.getLogger("model")

class Model:
    def __init__(self):
        self._lock = _threading.Lock()

        self._stores_by_id = dict()
        self._factories_by_id = dict()
        self._products_by_id = dict()
        self._items_by_id = dict()
        self._orders_by_id = dict()

        self.sizes = "small", "medium", "large"
        self.colors = "red", "green", "blue"

        Store(self, "Store 1", id="store-1")
        Store(self, "Store 2", id="store-2")
        Store(self, "Store 3", id="store-3")

        Factory(self, "Factory 1", id="factory-1")
        Factory(self, "Factory 2", id="factory-2")
        Factory(self, "Factory 3", id="factory-3")

        Product(self, "Cutlass", id="cutlass")
        Product(self, "Parrot", id="parrot")
        Product(self, "Pegleg", id="pegleg")

    def get_store(self, store_id):
        with self._lock:
            return self._stores_by_id.get(store_id)

    def get_factory(self, factory_id):
        with self._lock:
            return self._factories_by_id.get(factory_id)

    def get_product(self, product_id):
        with self._lock:
            return self._products_by_id.get(product_id)

    def get_item(self, item_id):
        with self._lock:
            return self._items_by_id.get(item_id)

    def add_item(self, item):
        _log.info(f"Adding {item}")

        with self._lock:
            self._items_by_id[item.id] = item

    def find_items(self, product, size, color):
        _log.info(f"Finding items ({product}, {size}, {color})")

        results = list()

        with self._lock:
            for item in self._items_by_id.values():
                if product is None or item.product is product:
                    if size is None or item.size == size:
                        if color is None or item.color == color:
                            results.append(item.data())

        return results

    def get_order(self, order_id):
        with self._lock:
            return self._orders_by_id.get(order_id)

    def add_order(self, order):
        _log.info(f"Adding {order}")

        with self._lock:
            self._orders_by_id[order.id] = order

    def find_orders(self):
        _log.info(f"Finding orders")

        results = list()

        with self._lock:
            for order in self._orders_by_id.values():
                results.append(order.data())

        return results

class Store:
    def __init__(self, model, name, id=None):
        self.model = model
        self.name = name
        self.id = id

        if self.id is None:
            self.id = _unique_id()

        with self.model._lock:
            self.model._stores_by_id[self.id] = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id},{self.name})"

class Factory:
    def __init__(self, model, name, id=None):
        self.model = model
        self.name = name
        self.id = id

        if self.id is None:
            self.id = _unique_id()

        with self.model._lock:
            self.model._factories_by_id[self.id] = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id},{self.name})"

class Product:
    def __init__(self, model, name, id=None):
        self.model = model
        self.name = name
        self.id = id

        if self.id is None:
            self.id = _unique_id()

        with self.model._lock:
            self.model._products_by_id[self.id] = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id},{self.name})"

class Item:
    def __init__(self, model, product, size, color, id=None):
        assert product in model._products_by_id.values()
        assert size in model.sizes
        assert color in model.colors

        self.id = id
        self.model = model
        self.product = product
        self.size = size
        self.color = color
        self.store = None # XXX Not here

        if self.id is None:
            self.id = _unique_id()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id},{self.product},{self.size},{self.color})"

    @staticmethod
    def load(model, data):
        product = model.get_product(data["product_id"])
        return Item(model, product, data["size"], data["color"], id=data["id"])

    def data(self):
        return {
            "id": self.id,
            "product_id": self.product.id,
            "size": self.size,
            "color": self.color,
            "store_id": (None if self.store is None else self.store.id), # XXX
        }

class Order:
    def __init__(self, model, product, size, color, id=None):
        assert product in model._products_by_id.values()
        assert size in model.sizes
        assert color in model.colors

        self.id = id
        self.model = model
        self.product = product
        self.size = size
        self.color = color

        self.id = id
        self.model = model

        if self.id is None:
            self.id = _unique_id()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id},{self.product},{self.size},{self.color})"

    @staticmethod
    def load(model, data):
        product = model.get_product(data["product_id"])
        return Order(model, product, data["size"], data["color"], id=data["id"])

    def data(self):
        return {
            "id": self.id,
            "product_id": self.product.id,
            "size": self.size,
            "color": self.color,
            # "store_id": (None if self.store is None else self.store.id),
        }

def _unique_id():
    uuid_bytes = _uuid.uuid4().bytes
    uuid_bytes = uuid_bytes[:4]

    return _binascii.hexlify(uuid_bytes).decode("utf-8")
