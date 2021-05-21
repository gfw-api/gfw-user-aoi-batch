from typing import Union

from datapump.globals import LOGGER
from datapump.jobs.geotrellis import FireAlertsGeotrellisJob, GeotrellisJob
from datapump.jobs.jobs import JobStatus
from datapump.jobs.version_update import UpdateRADDJob, UpdateGLADS2Job
from pydantic import parse_obj_as


def handler(event, context):
    job = parse_obj_as(Union[
        FireAlertsGeotrellisJob, GeotrellisJob, UpdateGLADS2Job, UpdateRADDJob
    ], event)

    try:
        LOGGER.info(f"Running next for job:\n{job.dict()}")
        job.next_step()
    except Exception as e:
        LOGGER.exception(e)
        job.status = JobStatus.failed

    return job.dict()
