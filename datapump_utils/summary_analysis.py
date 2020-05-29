import os
import json
import random
from enum import Enum

import boto3
from botocore.exceptions import ClientError

from datapump_utils.s3 import get_s3_path, s3_client

RESULT_BUCKET = os.environ["S3_BUCKET_PIPELINE"]
PUBLIC_SUBNET_IDS = json.loads(os.environ["PUBLIC_SUBNET_IDS"])
EC2_KEY_NAME = os.environ["EC2_KEY_NAME"]


class JobStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILURE = "FAILURE"


def submit_summary_batch_job(name, steps, instance_type, worker_count):
    master_instance_type = instance_type
    worker_instance_type = instance_type
    worker_instance_count = worker_count

    instances = _instances(
        name, master_instance_type, worker_instance_type, worker_instance_count
    )
    applications = _applications()
    configurations = _configurations(worker_instance_count)

    job_flow_id = _run_job_flow(name, instances, steps, applications, configurations)
    return job_flow_id


def get_summary_analysis_step(
    analysis, feature_url, result_url, jar, feature_type="feature", get_summary=True
):
    step_args = [
        "spark-submit",
        "--deploy-mode",
        "cluster",
        "--class",
        "org.globalforestwatch.summarystats.SummaryMain",
        jar,
        "--output",
        result_url,
        "--feature_type",
        feature_type,
        "--analysis",
        analysis,
    ]

    if not isinstance(feature_url, list):
        feature_url = [feature_url]

    for uri in feature_url:
        step_args.append("--features")
        step_args.append(uri)

    if "annualupdate" in analysis:
        step_args.append("--tcl")
    elif analysis == "gladalerts":
        step_args.append("--glad")

    if not get_summary:
        step_args.append("--change_only")

    return {
        "Name": analysis,
        "ActionOnFailure": "TERMINATE_CLUSTER",
        "HadoopJarStep": {"Jar": "command-runner.jar", "Args": step_args},
    }


def get_summary_analysis_steps(
    analyses, feature_src, feature_type, result_dir, get_summary, geotrellis_jar=None
):
    latest_jar = _get_geotrellis_jar(geotrellis_jar)
    steps = []

    for analysis in analyses:
        result_url = get_s3_path(RESULT_BUCKET, result_dir)
        steps.append(
            get_summary_analysis_step(
                analysis, feature_src, result_url, latest_jar, feature_type, get_summary
            )
        )

    return steps


def get_job_status(job_flow_id: str) -> JobStatus:
    emr_client = boto3.client("emr")
    cluster_description = emr_client.describe_cluster(ClusterId=job_flow_id)
    status = cluster_description["Cluster"]["Status"]

    if status["State"] == "TERMINATED":
        # only update AOIs atomically, so they don't get into a partially updated state if the
        # next nightly batch happens before we can fix partially updated AOIs
        if status["StateChangeReason"]["Code"] == "ALL_STEPS_COMPLETED":
            return JobStatus.SUCCESS
        else:
            return JobStatus.FAILURE
    elif status["State"] == "TERMINATED_WITH_ERRORS":
        return JobStatus.FAILURE
    else:
        return JobStatus.PENDING


def get_analysis_result_paths(result_bucket, result_directory, analysis_names):
    """
    Analysis result directories are named as <analysis>_<date>_<time>
    This creates a map of each analysis to its directory name so we know where to find
    the results for each analysis.
    """
    # adding '/' to result directory and listing with delimiter '/' will make boto list all the subdirectory
    # prefixes instead of all the actual objects
    response = s3_client().list_objects(
        Bucket=result_bucket, Prefix=result_directory + "/", Delimiter="/"
    )

    # get prefixes from response and remove trailing '/' for consistency
    analysis_result_paths = [
        prefix["Prefix"][:-1] for prefix in response["CommonPrefixes"]
    ]

    analysis_result_path_map = dict()
    for path in analysis_result_paths:
        for analysis in analysis_names:
            if analysis in os.path.basename(path):
                analysis_result_path_map[analysis] = path

    return analysis_result_path_map


def check_analysis_success(result_dir):
    try:
        # this will throw exception if success file isn't present
        s3_client().head_object(
            Bucket=RESULT_BUCKET, Key=f"{result_dir}/_SUCCESS",
        )

        return True
    except ClientError:
        return False


def get_dataset_result_path(analysis_result_path, aggregate_name, feature_type):
    return "{}/{}/{}".format(analysis_result_path, feature_type, aggregate_name)


def get_dataset_sources(results_path):
    object_list = s3_client().list_objects(Bucket=RESULT_BUCKET, Prefix=results_path)

    keys = [object["Key"] for object in object_list["Contents"]]
    csv_keys = filter(lambda key: key.endswith(".csv"), keys)

    # sometimes Spark creates empty partitions when it shuffles, but the GFW API will throw errors if you try
    # to upload an empty file, so just remove these from the list
    nonempty_csv_keys = []
    for key in csv_keys:
        meta = s3_client().head_object(Bucket=RESULT_BUCKET, Key=key)
        if meta["ContentLength"] > 0:
            nonempty_csv_keys.append(key)

    return [
        "https://{}.s3.amazonaws.com/{}".format(RESULT_BUCKET, key)
        for key in nonempty_csv_keys
    ]


def get_dataset_result_paths(result_dir, analyses, datasets, feature_type):
    analysis_result_paths = get_analysis_result_paths(
        RESULT_BUCKET, result_dir, analyses
    )
    dataset_result_paths = dict()

    for analysis, ds_ids in datasets.items():
        ds_keys = get_dataset_result_keys(ds_ids)
        for key_path, ds_id in ds_keys:
            if (
                feature_type != "gadm"
            ):  # TODO temp solution, need to deal with gadm output being different
                dataset_result_paths[
                    ds_id
                ] = f"{analysis_result_paths[analysis]}/{feature_type}/{key_path}"
            else:
                dataset_result_paths[
                    ds_id
                ] = f"{analysis_result_paths[analysis]}/{key_path}"

    return dataset_result_paths


def get_dataset_result_keys(ds_ids):
    results = []

    for dir_name, dir_val in ds_ids.items():
        # if another dir, go deeper
        if isinstance(dir_val, dict):
            dir_keys = get_dataset_result_keys(dir_val)
            results += [
                (f"{dir_name}/{dir_path}", dir_id) for dir_path, dir_id in dir_keys
            ]
        else:
            results.append((dir_name, dir_val))

    return results


def _run_job_flow(name, instances, steps, applications, configurations):
    client = boto3.client("emr", region_name="us-east-1")
    response = client.run_job_flow(
        Name=name,
        ReleaseLabel="emr-5.24.0",
        LogUri=f"s3://{RESULT_BUCKET}/geotrellis/logs",  # TODO should this be param?
        Instances=instances,
        Steps=steps,
        Applications=applications,
        Configurations=configurations,
        VisibleToAllUsers=True,
        JobFlowRole=os.environ["EMR_INSTANCE_PROFILE"],
        ServiceRole=os.environ["EMR_SERVICE_ROLE"],
        Tags=[
            {"Key": "Project", "Value": "Global Forest Watch"},
            {"Key": "Job", "Value": "GeoTrellis Summary Statistics"},
        ],  # flake8 --ignore
    )

    return response["JobFlowId"]


def _instances(name, master_instance_type, worker_instance_type, worker_instance_count):
    return {
        "InstanceGroups": [
            {
                "Name": "{}-master".format(name),
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": master_instance_type,
                "InstanceCount": 1,
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "VolumeType": "gp2",
                                "SizeInGB": 10,
                            },
                            "VolumesPerInstance": 1,
                        }
                    ],
                    "EbsOptimized": True,
                },
            },
            {
                "Name": "{}-cores".format(name),
                "Market": "SPOT",
                "InstanceRole": "CORE",
                # "BidPrice": "0.532",
                "InstanceType": worker_instance_type,
                "InstanceCount": worker_instance_count,
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "VolumeType": "gp2",
                                "SizeInGB": 10,
                            },
                            "VolumesPerInstance": 1,
                        }
                    ],
                    "EbsOptimized": True,
                },
            },
        ],
        "Ec2KeyName": EC2_KEY_NAME,
        "KeepJobFlowAliveWhenNoSteps": False,
        "TerminationProtected": False,
        "Ec2SubnetId": random.choice(PUBLIC_SUBNET_IDS),
    }


def _applications():
    return [
        {"Name": "Spark"},
        {"Name": "Zeppelin"},
        {"Name": "Ganglia"},
    ]


def _configurations(worker_instance_count):
    return [
        {
            "Classification": "spark",
            "Properties": {"maximizeResourceAllocation": "true"},
            "Configurations": [],
        },
        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.executor.memory": "6G",
                "spark.driver.memory": "6G",
                "spark.driver.cores": "1",
                "spark.driver.maxResultSize": "3G",
                "spark.rdd.compress": "true",
                "spark.executor.cores": "1",
                "spark.sql.shuffle.partitions": str((70 * worker_instance_count) - 1),
                "spark.shuffle.spill.compress": "true",
                "spark.shuffle.compress": "true",
                "spark.default.parallelism": str((70 * worker_instance_count) - 1),
                "spark.shuffle.service.enabled": "true",
                "spark.executor.extraJavaOptions": "-XX:+UseParallelGC -XX:+UseParallelOldGC -XX:OnOutOfMemoryError='kill -9 %p'",
                "spark.executor.instances": str((7 * worker_instance_count) - 1),
                "spark.yarn.executor.memoryOverhead": "1G",
                "spark.dynamicAllocation.enabled": "false",
                "spark.driver.extraJavaOptions": "-XX:+UseParallelGC -XX:+UseParallelOldGC -XX:OnOutOfMemoryError='kill -9 %p'",
            },
            "Configurations": [],
        },
        {
            "Classification": "yarn-site",
            "Properties": {
                "yarn.nodemanager.pmem-check-enabled": "false",
                "yarn.resourcemanager.am.max-attempts": "1",
                "yarn.nodemanager.vmem-check-enabled": "false",
            },
            "Configurations": [],
        },
    ]


def _get_geotrellis_jar(geotrellis_jar=None):
    if geotrellis_jar:
        return geotrellis_jar
    elif "GEOTRELLIS_JAR" in os.environ:
        jar = os.environ["GEOTRELLIS_JAR"]
    else:
        raise ValueError("Environment Variable 'GEOTRELLIS_JAR' is not set")

    return jar
