import os

from .function import (
    secret_suffix,
    geostore_to_wkb,
    get_geostore,
    get_geostore_ids,
    get_pending_areas,
)

os.environ["ENV"] = "test"

AREAS = {
    "data": [
        {
            "type": "area",
            "id": "59513a96de7e770010a400f5",
            "attributes": {
                "name": "testy",
                "application": "gfw",
                "geostore": "cfe38f3450bdc9ca8180733443c2a3dd",
                "userId": "5894720da19f5a00363bb7cf",
                "createdAt": "2017-06-26T16:47:18.132Z",
                "image": "https://s3.amazonaws.com/forest-watcher-files/areas-staging/59e73891-371c-4974-bf02-f87837b4f017.png",
                "datasets": [],
                "use": {"id": None, "name": None},
                "iso": {"country": None, "region": None},
                "admin": {},
                "templateId": None,
                "tags": [],
                "status": "pending",
                "public": True,
                "fireAlerts": True,
                "deforestationAlerts": True,
                "webhookUrl": "",
                "monthlySummary": True,
                "subscriptionId": "",
                "email": "",
                "language": "en",
            },
        },
        {
            "type": "area",
            "id": "599c36932574fb0010d4443c",
            "attributes": {
                "name": "Brazil Triangle",
                "application": "gfw",
                "geostore": "31a00f1d251f291ef82ca963cbc8dcf3",
                "userId": "58040bb24d98230b004c9617",
                "createdAt": "2017-08-22T13:50:11.261Z",
                "image": "https://s3.amazonaws.com/forest-watcher-files/areas/420625de-760b-46e0-99b6-5815b8864e49.png",
                "datasets": [],
                "use": {},
                "iso": {},
                "admin": {},
                "tags": [],
                "status": "pending",
                "public": True,
                "fireAlerts": False,
                "deforestationAlerts": False,
                "webhookUrl": "",
                "monthlySummary": False,
                "subscriptionId": "",
                "email": "",
                "language": "en",
            },
        },
    ]
}

GEOSTORE_IDS = ["cfe38f3450bdc9ca8180733443c2a3dd", "31a00f1d251f291ef82ca963cbc8dcf3"]

GEOSTORE = {
    "data": [
        {
            "geostoreId": "069b603da1c881cf0fc193c39c3687bb",
            "geostore": {
                "data": {
                    "type": "geoStore",
                    "id": "069b603da1c881cf0fc193c39c3687bb",
                    "attributes": {
                        "geojson": {
                            "features": [
                                {
                                    "type": "Feature",
                                    "geometry": {
                                        "type": "Polygon",
                                        "coordinates": [
                                            [
                                                [
                                                    8.923_828_125_016_8,
                                                    9.556_965_798_610_79,
                                                ],
                                                [
                                                    12.791_015_625_021_4,
                                                    8.689_186_410_236_46,
                                                ],
                                                [
                                                    8.923_828_125_016_8,
                                                    4.849_697_804_134_93,
                                                ],
                                                [
                                                    8.923_828_125_016_8,
                                                    9.556_965_798_610_79,
                                                ],
                                            ]
                                        ],
                                    },
                                }
                            ],
                            "crs": {},
                            "type": "FeatureCollection",
                        },
                        "hash": "069b603da1c881cf0fc193c39c3687bb",
                        "provider": {},
                        "areaHa": 11_186_986.783_767_128,
                        "bbox": [
                            8.923_828_125_016_8,
                            4.849_697_804_134_93,
                            12.791_015_625_021_4,
                            9.556_965_798_610_79,
                        ],
                        "lock": False,
                        "info": {"use": {}},
                    },
                }
            },
        },
        {
            "geostoreId": "0883910a878fdda456dbd72ec151126e",
            "geostore": {
                "data": {
                    "type": "geoStore",
                    "id": "0883910a878fdda456dbd72ec151126e",
                    "attributes": {
                        "geojson": {
                            "features": [
                                {
                                    "properties": None,
                                    "type": "Feature",
                                    "geometry": {
                                        "type": "MultiPolygon",
                                        "coordinates": [
                                            [
                                                [
                                                    [12.749, -1.8725],
                                                    [12.7433, -1.8689],
                                                    [12.7333, -1.8648],
                                                    [12.7221, -1.8644],
                                                    [12.6855, -1.8744],
                                                    [12.6837, -1.8767],
                                                    [12.6501, -1.882],
                                                    [12.6261, -1.8791],
                                                    [12.6144, -1.8754],
                                                    [12.5908, -1.8644],
                                                    [12.5718, -1.8583],
                                                    [12.5618, -1.8592],
                                                    [12.5563, -1.8661],
                                                    [12.5504, -1.885],
                                                    [12.5436, -1.8965],
                                                    [12.5351, -1.9009],
                                                    [12.5207, -1.9014],
                                                    [12.485, -1.8885],
                                                    [12.4715, -1.8743],
                                                    [12.4621, -1.87],
                                                    [12.4541, -1.87],
                                                    [12.4522, -1.8614],
                                                    [12.4425, -1.8578],
                                                    [12.4325, -1.8569],
                                                    [12.4122, -1.8569],
                                                    [12.3617, -1.8636],
                                                    [12.3422, -1.8642],
                                                    [12.3225, -1.8567],
                                                    [12.3108, -1.8536],
                                                    [12.2797, -1.8411],
                                                    [12.24, -1.8289],
                                                    [12.2186, -1.8208],
                                                    [12.2092, -1.8164],
                                                    [12.1992, -1.8086],
                                                    [12.1761, -1.7883],
                                                    [12.1669, -1.7786],
                                                    [12.1472, -1.7639],
                                                    [12.1283, -1.7447],
                                                    [12.09, -1.6867],
                                                    [12.0686, -1.6572],
                                                    [12.0589, -1.6492],
                                                    [12.0489, -1.6467],
                                                    [12.0389, -1.6456],
                                                    [12.0292, -1.6456],
                                                    [12.0244, -1.6381],
                                                    [12.0147, -1.6139],
                                                    [12.0136, -1.6081],
                                                    [12.0144, -1.5953],
                                                    [12.0167, -1.5839],
                                                    [12.0225, -1.5756],
                                                    [12.03, -1.5697],
                                                    [12.0364, -1.5619],
                                                    [12.0383, -1.5572],
                                                    [12.0414, -1.5533],
                                                    [12.0428, -1.5478],
                                                    [12.045, -1.5431],
                                                    [12.0469, -1.5183],
                                                    [12.0442, -1.4875],
                                                    [12.0422, -1.4758],
                                                    [12.035, -1.4556],
                                                    [12.0261, -1.4233],
                                                    [12.0272, -1.4033],
                                                    [12.0267, -1.3972],
                                                    [12.0228, -1.3878],
                                                    [12.0139, -1.375],
                                                    [12.0122, -1.37],
                                                    [11.9989, -1.3492],
                                                    [11.9919, -1.3422],
                                                    [11.98, -1.3331],
                                                    [11.9556, -1.3175],
                                                    [11.9367, -1.3089],
                                                    [11.9311, -1.3075],
                                                    [11.9167, -1.3011],
                                                    [11.9047, -1.2925],
                                                    [11.8725, -1.2603],
                                                    [11.8528, -1.2453],
                                                    [11.8397, -1.2375],
                                                    [11.8236, -1.2264],
                                                    [11.8133, -1.2158],
                                                    [11.8108, -1.2117],
                                                    [11.7981, -1.1969],
                                                    [11.7903, -1.1844],
                                                    [11.7867, -1.1808],
                                                    [11.7761, -1.1642],
                                                    [11.7728, -1.1608],
                                                    [11.7647, -1.1483],
                                                    [11.7569, -1.1289],
                                                    [11.7544, -1.1181],
                                                    [11.755, -1.0906],
                                                    [11.7558, -1.0775],
                                                    [11.7592, -1.0664],
                                                    [11.7542, -1.0619],
                                                    [11.7439, -1.06],
                                                    [11.7247, -1.0689],
                                                    [11.7053, -1.0808],
                                                    [11.6947, -1.0861],
                                                    [11.6758, -1.0997],
                                                    [11.6658, -1.1086],
                                                    [11.6553, -1.115],
                                                    [11.6358, -1.1164],
                                                    [11.6261, -1.1183],
                                                    [11.5961, -1.1344],
                                                    [11.5856, -1.1325],
                                                    [11.5761, -1.1272],
                                                    [11.5661, -1.125],
                                                    [11.5556, -1.1258],
                                                    [11.5461, -1.1206],
                                                    [11.5506, -1.1111],
                                                    [11.5508, -1.1017],
                                                    [11.5408, -1.0939],
                                                    [11.5528, -1.0744],
                                                    [11.5558, -1.0639],
                                                    [11.555, -1.0539],
                                                    [11.5411, -1.0047],
                                                    [11.5333, -0.9947],
                                                    [11.5242, -0.9875],
                                                    [11.5147, -0.9781],
                                                    [11.5097, -0.9683],
                                                    [11.5036, -0.9486],
                                                    [11.5033, -0.9392],
                                                    [11.5064, -0.9297],
                                                    [11.5036, -0.9189],
                                                    [11.4972, -0.9092],
                                                    [11.4967, -0.8994],
                                                    [11.4989, -0.8792],
                                                    [11.5022, -0.8594],
                                                    [11.5036, -0.8394],
                                                    [11.5061, -0.8286],
                                                    [11.5097, -0.8183],
                                                    [11.5172, -0.8089],
                                                    [11.5272, -0.7997],
                                                    [11.5381, -0.7919],
                                                    [11.5461, -0.7828],
                                                    [11.5625, -0.7536],
                                                    [11.6964, -0.7067],
                                                    [11.7194, -0.6964],
                                                    [11.7558, -0.6844],
                                                    [11.7706, -0.6781],
                                                    [11.8961, -0.6342],
                                                    [11.9178, -0.625],
                                                    [11.9919, -0.6],
                                                    [12.0131, -0.5911],
                                                    [12.0564, -0.5758],
                                                    [12.1025, -0.5569],
                                                    [12.1242, -0.5506],
                                                    [12.1686, -0.5347],
                                                    [12.2264, -0.5128],
                                                    [12.3236, -0.4775],
                                                    [12.3439, -0.4708],
                                                    [12.4281, -0.4392],
                                                    [12.4494, -0.4331],
                                                    [12.4539, -0.4214],
                                                    [12.4769, -0.3153],
                                                    [12.5481, -0.0039],
                                                    [12.5758, 0.1317],
                                                    [12.5847, 0.1692],
                                                    [12.5892, 0.1933],
                                                    [12.5992, 0.2283],
                                                    [12.6031, 0.2589],
                                                    [12.6089, 0.2847],
                                                    [12.6131, 0.2817],
                                                    [12.6272, 0.2622],
                                                    [12.6367, 0.2536],
                                                    [12.6464, 0.2469],
                                                    [12.6558, 0.245],
                                                    [12.6656, 0.2472],
                                                    [12.6758, 0.2558],
                                                    [12.6861, 0.2619],
                                                    [12.6964, 0.2639],
                                                    [12.7069, 0.2642],
                                                    [12.7172, 0.2689],
                                                    [12.7261, 0.2781],
                                                    [12.7322, 0.2881],
                                                    [12.7419, 0.2928],
                                                    [12.7531, 0.2728],
                                                    [12.7622, 0.2639],
                                                    [12.7722, 0.2603],
                                                    [12.7814, 0.2497],
                                                    [12.7819, 0.2397],
                                                    [12.79, 0.23],
                                                    [12.8086, 0.2192],
                                                    [12.8183, 0.2256],
                                                    [12.8281, 0.2344],
                                                    [12.8478, 0.2269],
                                                    [12.8675, 0.2214],
                                                    [12.8872, 0.2139],
                                                    [12.8969, 0.2119],
                                                    [12.9067, 0.2161],
                                                    [12.9264, 0.2325],
                                                    [12.9353, 0.2431],
                                                    [12.9356, 0.2531],
                                                    [12.9456, 0.2606],
                                                    [12.9536, 0.2511],
                                                    [12.9578, 0.2414],
                                                    [12.9781, 0.2317],
                                                    [12.9883, 0.2236],
                                                    [12.9986, 0.22],
                                                    [13.0089, 0.2172],
                                                    [13.0183, 0.2167],
                                                    [13.0294, 0.2186],
                                                    [13.0494, 0.2258],
                                                    [13.0589, 0.2214],
                                                    [13.0628, 0.2122],
                                                    [13.0692, 0.2025],
                                                    [13.0897, 0.1958],
                                                    [13.095, 0.1856],
                                                    [13.0908, 0.165],
                                                    [13.1011, 0.1458],
                                                    [13.115, 0.095],
                                                    [13.1219, 0.0853],
                                                    [13.1425, 0.0806],
                                                    [13.1517, 0.0733],
                                                    [13.1617, 0.0714],
                                                    [13.1714, 0.0617],
                                                    [13.1825, 0.0558],
                                                    [13.1928, 0.0533],
                                                    [13.2025, 0.0528],
                                                    [13.2119, 0.0572],
                                                    [13.2228, 0.0611],
                                                    [13.2325, 0.0542],
                                                    [13.2422, 0.0456],
                                                    [13.2519, 0.04],
                                                    [13.2617, 0.0394],
                                                    [13.2803, 0.0406],
                                                    [13.2833, 0.0286],
                                                    [13.285, -0.0117],
                                                    [13.2661, -0.0283],
                                                    [13.2572, -0.0478],
                                                    [13.2497, -0.0572],
                                                    [13.2494, -0.0678],
                                                    [13.2406, -0.0778],
                                                    [13.2375, -0.0872],
                                                    [13.2281, -0.0939],
                                                    [13.2183, -0.0994],
                                                    [13.2144, -0.1092],
                                                    [13.2247, -0.1147],
                                                    [13.2347, -0.1181],
                                                    [13.2394, -0.1278],
                                                    [13.2406, -0.1381],
                                                    [13.2481, -0.1692],
                                                    [13.2481, -0.1894],
                                                    [13.2492, -0.1997],
                                                    [13.2511, -0.2094],
                                                    [13.2544, -0.2192],
                                                    [13.2639, -0.2236],
                                                    [13.2931, -0.2281],
                                                    [13.3033, -0.2319],
                                                    [13.3083, -0.2417],
                                                    [13.3139, -0.2619],
                                                    [13.32, -0.2714],
                                                    [13.3283, -0.2808],
                                                    [13.3353, -0.2906],
                                                    [13.3372, -0.2956],
                                                    [13.3394, -0.2956],
                                                    [13.375, -0.3694],
                                                    [13.4433, -0.5036],
                                                    [13.55, -0.7214],
                                                    [13.5672, -0.7547],
                                                    [13.4994, -0.855],
                                                    [13.4336, -0.9544],
                                                    [13.3894, -1.0097],
                                                    [13.3622, -1.0397],
                                                    [13.3111, -1.1003],
                                                    [13.2617, -1.1622],
                                                    [13.2594, -1.1619],
                                                    [13.2556, -1.1589],
                                                    [13.2419, -1.1519],
                                                    [13.2364, -1.1506],
                                                    [13.2197, -1.1397],
                                                    [13.2031, -1.1356],
                                                    [13.19, -1.1269],
                                                    [13.1828, -1.1206],
                                                    [13.1697, -1.1128],
                                                    [13.1592, -1.1103],
                                                    [13.1567, -1.1111],
                                                    [13.1575, -1.1214],
                                                    [13.16, -1.1317],
                                                    [13.1644, -1.1414],
                                                    [13.1669, -1.1511],
                                                    [13.1675, -1.1603],
                                                    [13.1694, -1.1703],
                                                    [13.1728, -1.1803],
                                                    [13.1767, -1.1989],
                                                    [13.1772, -1.2086],
                                                    [13.1736, -1.2386],
                                                    [13.1733, -1.2581],
                                                    [13.1694, -1.2678],
                                                    [13.16, -1.2725],
                                                    [13.1389, -1.2778],
                                                    [13.1292, -1.2814],
                                                    [13.1194, -1.2872],
                                                    [13.1156, -1.2967],
                                                    [13.1161, -1.3067],
                                                    [13.1144, -1.3183],
                                                    [13.1083, -1.3278],
                                                    [13.0986, -1.3303],
                                                    [13.0881, -1.3319],
                                                    [13.0778, -1.3372],
                                                    [13.0697, -1.3472],
                                                    [13.0644, -1.3567],
                                                    [13.0578, -1.3658],
                                                    [13.0383, -1.3861],
                                                    [13.0281, -1.3925],
                                                    [13.0183, -1.3953],
                                                    [13.0089, -1.3947],
                                                    [12.9994, -1.3919],
                                                    [12.99, -1.3903],
                                                    [12.9706, -1.4064],
                                                    [12.9608, -1.4053],
                                                    [12.9514, -1.4014],
                                                    [12.9444, -1.4108],
                                                    [12.9458, -1.43],
                                                    [12.945, -1.4406],
                                                    [12.9389, -1.4508],
                                                    [12.9186, -1.4569],
                                                    [12.9008, -1.4786],
                                                    [12.8958, -1.4883],
                                                    [12.8964, -1.4978],
                                                    [12.8986, -1.5075],
                                                    [12.8989, -1.5172],
                                                    [12.8939, -1.5358],
                                                    [12.8858, -1.5453],
                                                    [12.8764, -1.5478],
                                                    [12.8714, -1.5575],
                                                    [12.8744, -1.5669],
                                                    [12.8706, -1.5761],
                                                    [12.8506, -1.5878],
                                                    [12.8431, -1.5992],
                                                    [12.8408, -1.6083],
                                                    [12.8408, -1.6178],
                                                    [12.8386, -1.6275],
                                                    [12.8317, -1.6378],
                                                    [12.8153, -1.6578],
                                                    [12.8106, -1.6675],
                                                    [12.8069, -1.6775],
                                                    [12.8044, -1.6889],
                                                    [12.8025, -1.7081],
                                                    [12.7942, -1.7186],
                                                    [12.7825, -1.7392],
                                                    [12.7736, -1.7503],
                                                    [12.7711, -1.7603],
                                                    [12.7825, -1.7894],
                                                    [12.7731, -1.7972],
                                                    [12.7633, -1.8072],
                                                    [12.7586, -1.8458],
                                                    [12.7556, -1.8583],
                                                    [12.749, -1.8725],
                                                ]
                                            ]
                                        ],
                                    },
                                }
                            ],
                            "crs": {},
                            "type": "FeatureCollection",
                        },
                        "hash": "0883910a878fdda456dbd72ec151126e",
                        "provider": {},
                        "areaHa": 2_922_934.707_296_363,
                        "bbox": [11.4967, -1.9014, 13.5672, 0.2928],
                        "lock": False,
                        "info": {
                            "use": {},
                            "iso": "GAB",
                            "name": "Ogooué-Lolo",
                            "id1": 7,
                            "gadm": "3.6",
                            "simplifyThresh": 0.0005,
                        },
                    },
                }
            },
        },
    ]
}


def test_secret_suffix():
    assert secret_suffix() == "staging"


def test_get_pending_areas(requests_mock):
    result = AREAS
    requests_mock.get(
        f"http://staging-api.globalforestwatch.org/v2/area?status=pending&all=True",
        json=result,
    )
    areas = get_pending_areas()

    assert areas == result


def test_get_geostore_ids():
    geostore_ids = get_geostore_ids(AREAS)
    assert geostore_ids == GEOSTORE_IDS


def test_get_geostore(requests_mock):
    requests_mock.post(
        f"https://staging-api.globalforestwatch.org/v1/geostore/find-by-ids",
        json=GEOSTORE,
    )
    geostore = get_geostore(GEOSTORE_IDS)
    assert geostore == GEOSTORE


def test_geostore_to_wkb():
    with geostore_to_wkb(GEOSTORE) as wkb:
        assert len(wkb.getvalue().split("\n")) == 32
