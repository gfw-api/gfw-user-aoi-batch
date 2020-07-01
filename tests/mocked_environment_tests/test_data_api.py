import os
import json

from tests.mock_environment.mock_environment import mock_environment
from moto import mock_s3, mock_secretsmanager

from lambdas.inject_fires_data.src.lambda_function import (
    handler,
    DATA_API_VIIRS_VERSION,
)
from datapump_utils.util import get_date_string


@mock_s3
@mock_secretsmanager
def test_inject_fires(requests_mock):
    mock_environment()
    os.environ["DATA_API_URI"] = "https://test.data-api.com"

    uri = f"https://test.data-api.com/meta/nasa_viirs_fire_alerts/{DATA_API_VIIRS_VERSION}"
    pending_resp = {"data": {"status": "pending"}}
    requests_mock.patch(uri, json=pending_resp)

    resp = handler(
        {
            "Output": json.dumps(
                {
                    "datasets": {"firealerts_viirs": {"all": "test_viirs_all_id"}},
                    "dataset_result_paths": {
                        "test_viirs_all_id": f"geotrellis/results/test/{get_date_string()}/firealerts_viirs_20191119_1245/geostore/all"
                    },
                }
            )
        },
        None,
    )

    assert resp["status"] == "PENDING"

    requests_mock.get(uri, json=pending_resp)
    resp = handler({"status": "PENDING"}, None)
    assert resp["status"] == "PENDING"

    saved_resp = {"data": {"status": "saved"}}

    requests_mock.get(uri, json=saved_resp)
    resp = handler({"status": "PENDING"}, None)
    assert resp["status"] == "SUCCESS"
