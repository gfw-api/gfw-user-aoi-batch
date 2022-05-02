from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from string import ascii_uppercase
from typing import Dict, List, Optional, Tuple, Type
from uuid import uuid1

import dateutil.tz as tz
from datapump.clients.data_api import DataApiClient

from ..clients.aws import get_s3_client, get_s3_path_parts
from ..clients.datapump_store import DatapumpConfig
from ..commands.analysis import FIRES_ANALYSES, AnalysisInputTable
from ..commands.sync import SyncType
from ..commands.version_update import RasterTileCacheParameters, RasterTileSetParameters
from ..globals import GLOBALS, LOGGER
from ..jobs.geotrellis import FireAlertsGeotrellisJob, GeotrellisJob, Job
from ..jobs.jobs import JobStatus
from ..jobs.version_update import RasterVersionUpdateJob
from ..sync.fire_alerts import get_tmp_result_path, process_active_fire_alerts
from ..sync.rw_areas import create_1x1_tsv
from ..util.gcs import get_gs_file_as_text, get_gs_files, get_gs_subfolders
from ..util.gpkg_util import update_geopackage
from ..util.models import ContentDateRange
from ..util.slack import slack_webhook


class Sync(ABC):
    @abstractmethod
    def __init__(self, sync_version: str):
        ...

    @abstractmethod
    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        ...


class FireAlertsSync(Sync):
    def __init__(self, sync_version: str):
        self.sync_version: str = sync_version
        self.fire_alerts_type: Optional[SyncType] = None
        self.fire_alerts_uri: Optional[str] = None

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        if self.fire_alerts_type is None:
            raise RuntimeError("No Alert type set")

        return [
            FireAlertsGeotrellisJob(
                id=str(uuid1()),
                status=JobStatus.starting,
                analysis_version=config.analysis_version,
                sync_version=self.sync_version,
                sync_type=config.sync_type,
                table=AnalysisInputTable(
                    dataset=config.dataset,
                    version=config.dataset_version,
                    analysis=config.analysis,
                ),
                features_1x1=config.metadata["features_1x1"],
                geotrellis_version=config.metadata["geotrellis_version"],
                alert_type=self.fire_alerts_type.value,
                alert_sources=[self.fire_alerts_uri],
                change_only=True,
                version_overrides=config.metadata.get("version_overrides", {}),
            )
        ]


class ViirsSync(FireAlertsSync):
    def __init__(self, sync_version: str):
        super(ViirsSync, self).__init__(sync_version)
        self.fire_alerts_type = SyncType.viirs
        self.fire_alerts_uri = process_active_fire_alerts(self.fire_alerts_type.value)

        # try to update geopackage, but still move on if it fails
        try:
            viirs_local_path = get_tmp_result_path("VIIRS")
            update_geopackage(viirs_local_path)
        except Exception as e:
            LOGGER.exception(e)
            slack_webhook(
                "ERROR", "Error updating fires geopackage. Check logs for more details."
            )


class ModisSync(FireAlertsSync):
    def __init__(self, sync_version: str):
        super(ModisSync, self).__init__(sync_version)
        self.fire_alerts_type = SyncType.modis
        self.fire_alerts_uri = process_active_fire_alerts(self.fire_alerts_type.value)


class GladSync(Sync):
    DATASET_NAME = "umd_glad_landsat_alerts"

    def __init__(self, sync_version: str):
        self.sync_version = sync_version
        self.should_sync_glad = self._check_for_new_glad()

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        if self.should_sync_glad:
            jobs = [
                GeotrellisJob(
                    id=str(uuid1()),
                    status=JobStatus.starting,
                    analysis_version=config.analysis_version,
                    sync_version=self.sync_version,
                    sync_type=config.sync_type,
                    table=AnalysisInputTable(
                        dataset=config.dataset,
                        version=config.dataset_version,
                        analysis=config.analysis,
                    ),
                    features_1x1=config.metadata["features_1x1"],
                    geotrellis_version=config.metadata["geotrellis_version"],
                    change_only=True,
                    version_overrides=config.metadata.get("version_overrides", {}),
                )
            ]

            if config.dataset == "gadm":
                jobs.append(
                    RasterVersionUpdateJob(
                        id=str(uuid1()),
                        status=JobStatus.starting,
                        dataset=self.DATASET_NAME,
                        version=self.sync_version,
                        tile_set_parameters=RasterTileSetParameters(
                            source_uri=[
                                f"s3://{GLOBALS.s3_bucket_data_lake}/{self.DATASET_NAME}/raw/tiles.geojson"
                            ],
                            grid="10/100000",
                            data_type="uint16",
                            pixel_meaning="date_conf",
                            union_bands=True,
                            compute_stats=False,
                            timeout_sec=21600,
                            no_data=0,
                        ),
                        content_date_range=ContentDateRange(
                            min="2014-12-31",  # FIXME: Change for collection 2?
                            max="2021-12-31",  # TODO: Set to str(date.today()) when GLAD starts updating again
                        ),
                    )
                )

            return jobs
        else:
            return []

    def _check_for_new_glad(self):
        bucket, path = get_s3_path_parts(GLOBALS.s3_glad_path)
        response = get_s3_client().get_object(
            Bucket=bucket, Key=f"{path}/events/status"
        )

        last_modified_datetime = response["LastModified"]
        status = response["Body"].read().strip().decode("utf-8")
        one_day_ago = datetime.now(tz.UTC) - timedelta(hours=24)

        stati = ["COMPLETED", "SAVED", "HADOOP RUNNING", "HADOOP FAILED"]
        return (status in stati) and (
            one_day_ago <= last_modified_datetime <= datetime.now(tz.UTC)
        )


class IntegratedAlertsSync(Sync):
    """
    Defines jobs to create new integrated alerts assets once a source alert dataset is updated.
    """

    DATASET_NAME = "gfw_integrated_alerts"
    SOURCE_DATASETS = [
        "umd_glad_landsat_alerts",
        "umd_glad_sentinel2_alerts",
        "wur_radd_alerts",
    ]

    # First filter for nodata by multiplying everything by
    # (((A.data) > 0) | ((B.data) > 0) | ((C.data) > 0))
    # Now to establish the combined confidence. We take 10000 and add
    # a maximum of 30000 for multiple alerts, otherwise 10000 for
    # low confidence and 20000 for high confidence single alerts. It looks
    # like taking the max of that and 0 is unnecessary because we already
    # filtered for nodata.
    # Next add the day. We want the minimum (earliest) day of the three
    # systems. Because we can't easily take the minimum of the date and avoid
    # 0 being the nodata value, subtract the day from the maximum 16-bit
    # value (65535) and take the max.
    _INPUT_CALC = """np.ma.array(
        (
            (((A.data) > 0) | ((B.data) > 0) | ((C.data) > 0))
            * (
                10000
                + 10000
                * np.where(
                    ((A.data // 10000) + (B.data // 10000) + (C.data // 10000)) > 3,
                    3,
                    np.maximum(
                        ((A.data // 10000) + (B.data // 10000) + (C.data // 10000)) - 1,
                        0,
                    ),
                ).astype(np.uint16)
                + (
                    65535
                    - np.maximum.reduce(
                        [
                            (
                                ((A.data) > 0)
                                * ((65535 - ((A.data) % 10000)).astype(np.uint16))
                            ),
                            (
                                ((B.data) > 0)
                                * ((65535 - ((B.data) % 10000)).astype(np.uint16))
                            ),
                            (
                                ((C.data) > 0)
                                * ((65535 - ((C.data) % 10000)).astype(np.uint16))
                            ),
                        ]
                    )
                )
            )
        ),
        mask=False,
    )"""
    INPUT_CALC = " ".join(_INPUT_CALC.split())

    def __init__(self, sync_version: str):
        self.sync_version = sync_version

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        """
        Creates two jobs for sync:
        1) Creates the integrated raster layers and assets. This includes
            a) A one band raster tile set where the values consist of the date
             of first detection by one of the three alert systems and their
             combined confidence for that pixel.
            b) A tile cache, using the special date_conf_intensity_multi_8 symbology
        2) Creates a Geotrellis job for integrated alerts. This can be done in
         parallel with 1) because it also uses the source datasets directly
        """

        latest_versions = self._get_latest_versions()
        source_uris = [
            f"s3://{GLOBALS.s3_bucket_data_lake}/{dataset}/{version}/raster/epsg-4326/10/100000/date_conf/geotiff/tiles.geojson"
            for dataset, version in latest_versions.items()
        ]

        if self._should_update(latest_versions):
            jobs = []

            if config.dataset == "gadm":
                jobs.append(
                    RasterVersionUpdateJob(
                        id=str(uuid1()),
                        status=JobStatus.starting,
                        dataset=self.DATASET_NAME,
                        version=self.sync_version,
                        tile_set_parameters=RasterTileSetParameters(
                            source_uri=source_uris,
                            calc=self.INPUT_CALC,
                            grid="10/100000",
                            data_type="uint16",
                            no_data=0,
                            pixel_meaning="date_conf",
                            band_count=1,
                            union_bands=True,
                            compute_stats=False,
                            timeout_sec=21600,
                        ),
                        tile_cache_parameters=RasterTileCacheParameters(
                            max_zoom=14,
                            resampling="med",
                            symbology={"type": "date_conf_intensity_multi_8"},
                        ),
                        content_date_range=ContentDateRange(
                            min="2014-12-31", max=str(date.today())
                        ),
                    )
                )
            jobs.append(
                GeotrellisJob(
                    id=str(uuid1()),
                    status=JobStatus.starting,
                    analysis_version=config.analysis_version,
                    sync_version=self.sync_version,
                    sync_type=config.sync_type,
                    table=AnalysisInputTable(
                        dataset=config.dataset,
                        version=config.dataset_version,
                        analysis=config.analysis,
                    ),
                    features_1x1=config.metadata["features_1x1"],
                    geotrellis_version=config.metadata["geotrellis_version"],
                )
            )

            return jobs
        else:
            return []

    def _get_latest_versions(self) -> Dict[str, str]:
        client = DataApiClient()
        return {ds: client.get_latest_version(ds) for ds in self.SOURCE_DATASETS}

    def _should_update(self, latest_versions: Dict[str, str]) -> bool:
        """
        Check if any of the dependent deforestation alert layers have created
        a new version in the last 24 hours on the API
        """
        client = DataApiClient()

        versions = [
            client.get_version(ds, latest_versions[ds]) for ds in self.SOURCE_DATASETS
        ]
        last_updates = [
            datetime.fromisoformat(v["created_on"]).replace(tzinfo=tz.UTC)
            for v in versions
        ]

        one_day_ago = datetime.now(tz.UTC) - timedelta(hours=24)

        if any([last_update > one_day_ago for last_update in last_updates]):
            return True

        return False


class DeforestationAlertsSync(Sync):
    """
    Defines jobs to create new deforestation alerts assets once a new release is available.
    """

    @property
    @abstractmethod
    def dataset_name(self):
        ...

    @property
    @abstractmethod
    def source_bucket(self):
        ...

    @property
    @abstractmethod
    def source_prefix(self):
        ...

    @property
    @abstractmethod
    def input_calc(self):
        ...

    @property
    @abstractmethod
    def number_of_tiles(self):
        ...

    @property
    @abstractmethod
    def grid(self):
        ...

    def __init__(self, sync_version: str):
        self.sync_version = sync_version

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        """
        Creates the WUR RADD raster layer and assets
        """

        latest_api_version = self.get_latest_api_version(self.dataset_name)
        latest_release, source_uris = self.get_latest_release()

        if float(latest_api_version.lstrip("v")) >= float(latest_release.lstrip("v")):
            return []

        return [self.get_raster_job(latest_release, source_uris)]

    def get_raster_job(
        self, version: str, source_uris: List[str]
    ) -> RasterVersionUpdateJob:
        version_dt: str = str(self.parse_version_as_dt(version).date())

        return RasterVersionUpdateJob(
            id=str(uuid1()),
            status=JobStatus.starting,
            dataset=self.dataset_name,
            version=version,
            tile_set_parameters=RasterTileSetParameters(
                source_uri=source_uris,
                calc=self.input_calc,
                grid=self.grid,
                data_type="uint16",
                no_data=0,
                pixel_meaning="date_conf",
                band_count=1,
                compute_stats=False,
            ),
            tile_cache_parameters=RasterTileCacheParameters(
                max_zoom=14,
                resampling="nearest",
                symbology={"type": "date_conf_intensity"},
            ),
            content_date_range=ContentDateRange(min="2020-01-01", max=str(version_dt)),
        )

    @abstractmethod
    def get_latest_release(self) -> Tuple[str, List[str]]:
        ...

    @staticmethod
    def parse_version_as_dt(version: str) -> datetime:
        # Technically this has a Y10K bug
        release_date = version.lstrip("v")
        assert (
            len(release_date) == 8
        ), "Possibly malformed version folder name in RADD GCS bucket!"
        year, month, day = (
            int(release_date[:4]),
            int(release_date[4:6]),
            int(release_date[6:]),
        )
        return datetime(year, month, day)

    @staticmethod
    def get_latest_api_version(dataset_name: str) -> str:
        """
        Get the version of the latest release in the Data API
        """
        client = DataApiClient()
        return client.get_latest_version(dataset_name)


class RADDAlertsSync(DeforestationAlertsSync):
    """
    Defines jobs to create new RADD alerts assets once a new release is available.
    """

    dataset_name = "wur_radd_alerts"
    source_bucket = "gfw_gee_export"
    source_prefix = "wur_radd_alerts/"
    input_calc = "(A >= 20000) * (A < 40000) * A"
    number_of_tiles = 175
    grid = "10/100000"

    def __init__(self, sync_version: str):
        super().__init__(sync_version)

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        return super().build_jobs(config)

    def get_latest_release(self) -> Tuple[str, List[str]]:
        """
        Get the version of the latest *complete* release in GCS
        """

        LOGGER.info(
            f"Looking for RADD folders in gs://{self.source_bucket}/{self.source_prefix}"
        )
        versions: List[str] = get_gs_subfolders(self.source_bucket, self.source_prefix)

        # Shouldn't need to look back through many, so avoid the corner
        # case that would check every previous version when run right after
        # increasing NUMBER_OF_TILES and hitting GCS as a new release is being
        # uploaded

        LOGGER.info(f"{self.dataset_name} versions: {versions}")
        for version in sorted(versions, reverse=True)[:3]:
            version_prefix = f"{self.source_prefix}{version}"
            LOGGER.info(
                f"Looking for RADD tiles in gs://{self.source_bucket}/{version_prefix}"
            )

            version_tiles: int = len(
                get_gs_files(self.source_bucket, version_prefix, extensions=[".tif"])
            )

            LOGGER.info(
                f"Found {version_tiles} RADD tiles in gs://{self.source_bucket}/{version_prefix}"
            )
            if version_tiles > self.number_of_tiles:
                raise Exception(
                    f"Found {version_tiles} TIFFs in latest {self.dataset_name} GCS folder, which is "
                    f"greater than the expected {self.number_of_tiles}. "
                    "If the extent has grown, update NUMBER_OF_TILES value."
                )
            elif version_tiles == self.number_of_tiles:
                latest_release = version.rstrip("/")
                source_uris = [
                    f"gs://{self.source_bucket}/{self.source_prefix}{latest_release}"
                ]

                return latest_release, source_uris

        # We shouldn't get here
        raise Exception(f"No complete {self.dataset_name} versions found in GCS!")


class GLADLAlertsSync(DeforestationAlertsSync):
    """
    Defines jobs to create new RADD alerts assets once a new release is available.
    """

    dataset_name = "umd_glad_landsat_alerts"
    source_bucket = "earthenginepartners-hansen"
    source_prefix = "GLADalert/C2"
    number_of_tiles = 115
    grid = "10/40000"
    start_year = 2021

    @property
    def input_calc(self):
        """
        Calc string is
        """
        today = self.get_today()

        calc_strings = []
        prev_conf_bands = []
        bands = iter(ascii_uppercase)

        for year in range(self.start_year, today.year + 1):
            year_start = self.get_days_since_2015(year)
            conf_band = next(bands)

            # earlier years should override later years for overlapping pixels
            prev_conf_calc_string = "".join(
                [f"({band} == 0) * " for band in prev_conf_bands]
            )

            date_band = next(bands)
            calc_strings.append(
                f"({prev_conf_calc_string}({conf_band} > 0) * (20000 + 10000 * ({conf_band} > 1) + {year_start} + {date_band}))"
            )
            prev_conf_bands.append(conf_band)

        calc_string = f"np.ma.array({' + '.join(calc_strings)}, mask=False)"
        return calc_string

    def get_latest_release(self) -> Tuple[str, List[str]]:
        """
        Get the version of the latest *complete* release in GCS
        """

        today_prefix = self.get_today().strftime("%Y/%m_%d")
        version_tiles: List[str] = get_gs_files(
            self.source_bucket,
            f"{self.source_prefix}/{today_prefix}/alertDate22",
            extensions=[".tif"],
        )

        if len(version_tiles) > self.number_of_tiles:
            raise Exception(
                f"Found {version_tiles} TIFFs in latest {self.dataset_name} GCS folder, which is "
                f"greater than the expected {self.number_of_tiles}. "
                "If the extent has grown, update NUMBER_OF_TILES value."
            )
        elif len(version_tiles) == self.number_of_tiles:
            today = self.get_today()

            source_uris = []
            for year in range(self.start_year, today.year + 1):
                year_suffix = str(year)[2:4]

                if year == today.year or (year == today.year - 1 and today.month < 7):
                    # these rasters are still being updated
                    source_uris += [
                        f"gs://{self.source_bucket}/{self.source_prefix}/{today_prefix}/alert{year_suffix}*",
                        f"gs://{self.source_bucket}/{self.source_prefix}/{today_prefix}/alertDate{year_suffix}*",
                    ]
                else:
                    # otherwise, use final raster for that year
                    source_uris += [
                        f"gs://{self.source_bucket}/{self.source_prefix}/{year}/final/alert{year_suffix}*",
                        f"gs://{self.source_bucket}/{self.source_prefix}/{year}/final/alertDate{year_suffix}*",
                    ]

            return self.sync_version, source_uris

        else:
            raise Exception(f"No complete {self.dataset_name} versions found in GCS!")

    @staticmethod
    def get_days_since_2015(year: int) -> int:
        year_date = date(year=year, month=1, day=1)
        start_date = date(year=2015, month=1, day=1)
        return (year_date - start_date).days

    @staticmethod
    def get_today():
        return date.today()


class GLADS2AlertsSync(DeforestationAlertsSync):
    """
    Defines jobs to create new RADD alerts assets once a new release is available.
    """

    dataset_name = "umd_glad_sentinel2_alerts"
    source_bucket = "earthenginepartners-hansen"
    source_prefix = "S2alert"
    input_calc = "(A > 0) * (20000 + 10000 * (A > 1) + B + 1461)"
    number_of_tiles = 18
    grid = "10/100000"

    def get_latest_release(self) -> Tuple[str, List[str]]:
        """
        Get the version of the latest *complete* release in GCS
        """

        # Raw tiles are just updated in-place
        source_uri = [
            f"gs://{self.source_bucket}/{self.source_prefix}/alert",
            f"gs://{self.source_bucket}/{self.source_prefix}/alertDate",
        ]

        # This file is updated once tiles are updated
        upload_date_text = get_gs_file_as_text(
            self.source_bucket, f"{self.source_prefix}/uploadDate.txt"
        )

        # Example string: "Updated Fri Apr 15 14:27:01 2022 UTC"
        upload_date = upload_date_text[12:-4]
        latest_release = datetime.strptime(upload_date, "%b %d %H:%M:%S %Y").strftime(
            "v%Y%m%d"
        )

        return latest_release, source_uri


class RWAreasSync(Sync):
    def __init__(self, sync_version: str):
        self.sync_version = sync_version
        self.features_1x1 = create_1x1_tsv(sync_version)

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        if self.features_1x1:
            kwargs = {
                "id": str(uuid1()),
                "status": JobStatus.starting,
                "analysis_version": config.analysis_version,
                "sync_version": self.sync_version,
                "table": AnalysisInputTable(
                    dataset=config.dataset,
                    version=config.dataset_version,
                    analysis=config.analysis,
                ),
                "features_1x1": self.features_1x1,
                "geotrellis_version": config.metadata["geotrellis_version"],
                "sync_type": config.sync_type,
                "version_overrides": config.metadata.get("version_overrides", {}),
            }

            if config.analysis in FIRES_ANALYSES:
                kwargs["alert_type"] = config.analysis
                return [FireAlertsGeotrellisJob(**kwargs)]
            else:
                return [GeotrellisJob(**kwargs)]
        else:
            return []


class Syncer:
    SYNCERS: Dict[SyncType, Type[Sync]] = {
        SyncType.viirs: ViirsSync,
        SyncType.modis: ModisSync,
        SyncType.rw_areas: RWAreasSync,
        SyncType.glad: GladSync,
        SyncType.integrated_alerts: IntegratedAlertsSync,
        SyncType.wur_radd_alerts: RADDAlertsSync,
    }

    def __init__(self, sync_types: List[SyncType], sync_version: str = None):
        self.sync_version: str = (
            sync_version if sync_version else self._get_latest_version()
        )
        self.syncers: Dict[SyncType, Sync] = {
            sync_type: self.SYNCERS[sync_type](self.sync_version)
            for sync_type in sync_types
        }

    @staticmethod
    def _get_latest_version():
        return f"v{datetime.now().strftime('%Y%m%d')}"

    def build_jobs(self, config: DatapumpConfig) -> List[Job]:
        """
        Build Job model based on sync type
        :param config: sync configuration
        :return: Job model, or None if there's no job to sync
        """
        sync_type = SyncType[config.sync_type]

        try:
            jobs = self.syncers[sync_type].build_jobs(config)
        except Exception:
            LOGGER.error(
                f"Could not generate jobs for sync type {sync_type} with config {config}"
            )
            # TODO report to slack?
            return []

        return jobs
