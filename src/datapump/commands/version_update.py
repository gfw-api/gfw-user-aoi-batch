from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import StrictInt

from datapump.util.models import StrictBaseModel


class NonNumericFloat(str, Enum):
    nan = "nan"


NoDataType = Union[StrictInt, NonNumericFloat]


class RasterTileSetParameters(StrictBaseModel):
    source_uri: List[str]
    calc: Optional[str]
    grid: str
    data_type: str
    no_data: Optional[Union[List[NoDataType], NoDataType]]
    pixel_meaning: str


class RasterTileCacheParameters(StrictBaseModel):
    symbology: Optional[Dict[str, Any]]
    max_zoom: int


class RasterVersionUpdateCommand(StrictBaseModel):
    command: str

    class RasterVersionUpdateParameters(StrictBaseModel):
        dataset: str
        version: str
        tile_set_parameters: RasterTileSetParameters
        tile_cache_parameters: RasterTileCacheParameters

    parameters: RasterVersionUpdateParameters