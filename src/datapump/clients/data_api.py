import json
import requests
from typing import List, Dict, Any
from pprint import pformat
from enum import Enum

from ..globals import DATA_API_URI, LOGGER
from ..util.exceptions import DataApiResponseError
from .rw_api import token


class ValidMethods(str, Enum):
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    get = "GET"


class DataApiClient:
    def __init__(self):
        LOGGER.info(f"Create data API client at URI: {DATA_API_URI}")

    def get_latest(self):
        pass

    def get_assets(self, dataset: str, version: str) -> List[Dict[str, Any]]:
        uri = f"{DATA_API_URI}/dataset/{dataset}/{version}/assets"
        return self._send_request(ValidMethods.get, uri)

    def get_1x1_asset(self, dataset: str, version: str) -> str:
        assets = self.get_assets(dataset, version)

        for asset in assets:
            if asset["asset_type"] == "1x1 grid":
                return asset["asset_uri"]

        raise ValueError(f"Dataset {dataset}/{version} missing 1x1 grid asset")

    def create_dataset_and_version(
        self,
        dataset: str,
        version: str,
        source_uris: List[str],
        indices: List[str],
        cluster: List[str],
        metadata: Dict[str, Any]={}
    ):
        try:
            self.get_dataset(dataset)
        except DataApiResponseError:
            self.create_dataset(dataset, metadata)

        self.create_version(dataset, version, source_uris, indices, cluster)

    def create_dataset(self, dataset: str, metadata: Dict[str, Any]={}):
        uri = f"{DATA_API_URI}/dataset/{dataset}"
        payload = {
            "metadata": metadata
        }

        return self._send_request(ValidMethods.put, uri, payload)

    def create_version(
        self,
        dataset: str,
        version: str,
        source_uris: List[str],
        indices: List[str],
        cluster: List[str],
    ) -> Dict[str, Any]:
        payload = {
            "creation_options": {
                "source_type": "table",
                "source_driver": "text",
                "source_uri": source_uris,
                "delimiter": "\t",
                "has_header": True,
                "indices": [{"index_type": "btree", "column_names": indices}],
                "cluster": {"index_type": "btree", "column_names": cluster},
            }
        }

        uri = f"{DATA_API_URI}/dataset/{dataset}/{version}"
        return self._send_request(ValidMethods.put, uri, payload)

    def append(self, dataset: str, version: str, source_uris: List[str]):
        payload = {"creation_options": {"source_uri": source_uris}}
        uri = f"{DATA_API_URI}/dataset/{dataset}/{version}/append"
        return self._send_request(ValidMethods.post, uri, payload)

    def get_version(self, dataset: str, version: str):
        uri = f"{DATA_API_URI}/dataset/{dataset}/{version}"
        return self._send_request(ValidMethods.get, uri)

    def get_dataset(self, dataset: str):
        uri = f"{DATA_API_URI}/dataset/{dataset}"
        return self._send_request(ValidMethods.get, uri)

    @staticmethod
    def _send_request(method: ValidMethods, uri: str, payload: Dict[str, Any]=None) -> Dict[str, Any]:
        LOGGER.info(
            f"Send Data API request:\n"
            f"\tURI: {uri}\n"
            f"\tMethod: {method.value}\n"
            f"\tPayload:{json.dumps(payload)}\n"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token()}",
        }

        if method == ValidMethods.post:
            resp = requests.post(uri, json=payload, headers=headers)
        elif method == ValidMethods.put:
            resp = requests.put(uri, json=payload, headers=headers)
        elif method == ValidMethods.patch:
            resp = requests.patch(uri, json=payload, headers=headers)
        elif method == ValidMethods.get:
            resp = requests.get(uri, headers=headers)

        if resp.status_code >= 300:
            error_msg = f"Data API responded with status code {resp.status_code}\n"
            try:
                body = resp.json()
                error_msg += pformat(body)
            finally:
                raise DataApiResponseError(error_msg)
        else:
            return resp.json()["data"]