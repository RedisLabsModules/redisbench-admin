import logging
import os
import sys
import tempfile

import boto3
import git
import paramiko
import pysftp
import redis
import redistimeseries.client as Client
from git import Repo
from jsonpath_ng import parse
from python_terraform import Terraform
from tqdm import tqdm


def viewBarSimple(a, b):
    res = a / int(b) * 100
    sys.stdout.write("\r    Complete precent: %.2f %%" % (res))
    sys.stdout.flush()


def copyFileToRemoteSetup(
    server_public_ip, username, private_key, local_file, remote_file
):
    logging.info(
        "\tCopying local file {} to remote server {}".format(local_file, remote_file)
    )
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(
        host=server_public_ip, username=username, private_key=private_key, cnopts=cnopts
    )
    srv.put(local_file, remote_file, callback=viewBarSimple)
    srv.close()
    logging.info("")


def getFileFromRemoteSetup(
    server_public_ip, username, private_key, local_file, remote_file
):
    logging.info(
        "\Retrieving remote file {} from remote server {} ".format(
            remote_file, server_public_ip
        )
    )
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(
        host=server_public_ip, username=username, private_key=private_key, cnopts=cnopts
    )
    srv.get(remote_file, local_file, callback=viewBarSimple)
    srv.close()
    logging.info("")


def executeRemoteCommands(server_public_ip, username, private_key, commands):
    res = []
    k = paramiko.RSAKey.from_private_key_file(private_key)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    logging.info("Connecting to remote server {}".format(server_public_ip))
    c.connect(hostname=server_public_ip, username=username, pkey=k)
    logging.info("Connected to remote server {}".format(server_public_ip))
    for command in commands:
        logging.info('Executing remote command "{}"'.format(command))
        stdin, stdout, stderr = c.exec_command(command)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        res.append([stdout, stderr])
    c.close()
    return res


def checkDatasetRemoteRequirements(
    benchmark_config, server_public_ip, username, private_key, remote_dataset_file
):
    for k in benchmark_config["dbconfig"]:
        if "dataset" in k:
            dataset = k["dataset"]
    if dataset is not None:
        copyFileToRemoteSetup(
            server_public_ip,
            username,
            private_key,
            dataset,
            remote_dataset_file,
        )


def setupRemoteEnviroment(
    tf: Terraform,
    tf_github_sha,
    tf_github_actor,
    tf_setup_name,
    tf_github_org,
    tf_github_repo,
    tf_triggering_env,
):
    # key    = "benchmarks/infrastructure/tf-oss-redisgraph-standalone-r5.tfstate"
    return_code, stdout, stderr = tf.init(
        capture_output=True,
        backend_config={
            "key": "benchmarks/infrastructure/{}.tfstate".format(tf_setup_name)
        },
    )
    return_code, stdout, stderr = tf.refresh()
    tf_output = tf.output()
    server_private_ip = tf_output["server_private_ip"]["value"][0]
    server_public_ip = tf_output["server_public_ip"]["value"][0]
    client_private_ip = tf_output["client_private_ip"]["value"][0]
    client_public_ip = tf_output["client_public_ip"]["value"][0]
    if (
        server_private_ip is not None
        or server_public_ip is not None
        or client_private_ip is not None
        or client_public_ip is not None
    ):
        logging.warning("Destroying previous setup")
        tf.destroy()
    return_code, stdout, stderr = tf.apply(
        skip_plan=True,
        capture_output=False,
        refresh=True,
        var={
            "github_sha": tf_github_sha,
            "github_actor": tf_github_actor,
            "setup_name": tf_setup_name,
            "github_org": tf_github_org,
            "github_repo": tf_github_repo,
            "triggering_env": tf_triggering_env,
        },
    )
    tf_output = tf.output()
    server_private_ip = tf_output["server_private_ip"]["value"][0]
    server_public_ip = tf_output["server_public_ip"]["value"][0]
    server_plaintext_port = 6379
    client_private_ip = tf_output["client_private_ip"]["value"][0]
    client_public_ip = tf_output["client_public_ip"]["value"][0]
    username = "ubuntu"
    return (
        return_code,
        username,
        server_private_ip,
        server_public_ip,
        server_plaintext_port,
        client_private_ip,
        client_public_ip,
    )


def extract_git_vars():
    github_repo = Repo("{}/../..".format(os.getcwd()))
    github_url = github_repo.remotes[0].config_reader.get("url")
    github_org_name = github_url.split("/")[-2]
    github_repo_name = github_url.split("/")[-1].split(".")[0]
    github_sha = github_repo.head.object.hexsha
    github_branch = github_repo.active_branch
    github_actor = github_repo.config_reader().get_value("user", "name")
    return github_org_name, github_repo_name, github_sha, github_actor, github_branch


def validateResultExpectations(
    benchmark_config, results_dict, result, expectations_key="expectations"
):
    for expectation in benchmark_config[expectations_key]:
        for comparison_mode, rules in expectation.items():
            for jsonpath, expected_value in rules.items():
                jsonpath_expr = parse(jsonpath)
                actual_value = float(jsonpath_expr.find(results_dict)[0].value)
                expected_value = float(expected_value)
                if comparison_mode == "eq":
                    if actual_value != expected_value:
                        result &= False
                        logging.error(
                            "Condition on {} {} {} {} is False. Failing test expectations".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
                    else:
                        logging.info(
                            "Condition on {} {} {} {} is True.".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
                if comparison_mode == "le":
                    if actual_value > expected_value:
                        result &= False
                        logging.error(
                            "Condition on {} {} {} {} is False. Failing test expectations".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
                    else:
                        logging.info(
                            "Condition on {} {} {} {} is True.".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
                if comparison_mode == "ge":
                    if actual_value < expected_value:
                        result &= False
                        logging.error(
                            "Condition on {} {} {} {} is False. Failing test expectations".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
                    else:
                        logging.info(
                            "Condition on {} {} {} {} is True.".format(
                                jsonpath,
                                actual_value,
                                comparison_mode,
                                expected_value,
                            )
                        )
    return result


def upload_artifacts_to_s3(
    artifacts, s3_bucket_name, s3_bucket_path, acl="public-read"
):
    logging.info("Uploading results to s3")
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3_bucket_name)
    progress = tqdm(unit="files", total=len(artifacts))
    for input in artifacts:
        object_key = "{bucket_path}{filename}".format(
            bucket_path=s3_bucket_path, filename=input
        )
        bucket.upload_file(input, object_key)
        object_acl = s3.ObjectAcl(s3_bucket_name, object_key)
        response = object_acl.put(ACL=acl)
        progress.update()
    progress.close()


def checkAndFixPemStr(EC2_PRIVATE_PEM):
    pem_str = EC2_PRIVATE_PEM.replace("-----BEGIN RSA PRIVATE KEY-----", "")
    pem_str = pem_str.replace("-----END RSA PRIVATE KEY-----", "")
    pem_str = pem_str.replace(" ", "\n")
    pem_str = "-----BEGIN RSA PRIVATE KEY-----\n" + pem_str
    pem_str = pem_str + "-----END RSA PRIVATE KEY-----\n"
    # remove any dangling whitespace
    pem_str = os.linesep.join([s for s in pem_str.splitlines() if s])
    return pem_str


def get_run_full_filename(
    start_time_str,
    deployment_type,
    github_org,
    github_repo,
    github_branch,
    test_name,
    github_sha,
):
    benchmark_output_filename = "{start_time_str}-{github_org}-{github_repo}-{github_branch}-{test_name}-{deployment_type}-{github_sha}.json".format(
        start_time_str=start_time_str,
        github_org=github_org,
        github_repo=github_repo,
        github_branch=github_branch,
        test_name=test_name,
        deployment_type=deployment_type,
        github_sha=github_sha,
    )
    return benchmark_output_filename


def fetchRemoteSetupFromConfig(remote_setup_config):
    branch = "master"
    repo = None
    path = None
    for remote_setup_property in remote_setup_config:
        if "repo" in remote_setup_property:
            repo = remote_setup_property["repo"]
        if "branch" in remote_setup_property:
            branch = remote_setup_property["branch"]
        if "path" in remote_setup_property:
            path = remote_setup_property["path"]
    # fetch terraform folder
    temporary_dir = tempfile.mkdtemp()
    logging.info(
        "Fetching infrastructure definition from git repo {}/{} (branch={})".format(
            repo, path, branch
        )
    )
    git.Repo.clone_from(repo, temporary_dir, branch=branch, depth=1)
    terraform_working_dir = temporary_dir
    if path is not None:
        terraform_working_dir += path
    return terraform_working_dir


def pushDataToRedisTimeSeries(rts: Client, branch_time_series_dict: dict):
    datapoint_errors = 0
    datapoint_inserts = 0
    for timeseries_name, time_series in branch_time_series_dict.items():
        try:
            logging.info(
                "Creating timeseries named {} with labels {}".format(
                    timeseries_name, time_series["labels"]
                )
            )
            rts.create(timeseries_name, labels=time_series["labels"])
        except redis.exceptions.ResponseError as e:
            logging.warning(
                "Timeseries named {} already exists".format(timeseries_name)
            )
            pass
        for timestamp, value in time_series["data"].items():
            try:
                rts.add(
                    timeseries_name,
                    timestamp,
                    value,
                    duplicate_policy="last",
                )
                datapoint_inserts += 1
            except redis.exceptions.ResponseError:
                logging.warning(
                    "Error while inserting datapoint ({} : {}) in timeseries named {}. ".format(
                        timestamp, value, timeseries_name
                    )
                )
                datapoint_errors += 1
                pass
    return datapoint_errors, datapoint_inserts


def extractPerBranchTimeSeriesFromResults(
    datapoints_timestamp: int,
    metrics: list,
    results_dict: dict,
    tf_github_branch: str,
    tf_github_org: str,
    tf_github_repo: str,
    deployment_type: str,
    test_name: str,
    tf_triggering_env: str,
):
    branch_time_series_dict = {}
    for jsonpath in metrics:
        jsonpath_expr = parse(jsonpath)
        metric_name = jsonpath[2:]
        metric_value = float(jsonpath_expr.find(results_dict)[0].value)
        # prepare tags
        # branch tags
        branch_tags = {
            "branch": str(tf_github_branch),
            "github_org": tf_github_org,
            "github_repo": tf_github_repo,
            "deployment_type": deployment_type,
            "test_name": test_name,
            "triggering_env": tf_triggering_env,
            "metric": metric_name,
        }
        ts_name = "ci.benchmarks.redislabs/{triggering_env}/{github_org}/{github_repo}/{test_name}/{deployment_type}/{branch}/{metric}".format(
            branch=str(tf_github_branch),
            github_org=tf_github_org,
            github_repo=tf_github_repo,
            deployment_type=deployment_type,
            test_name=test_name,
            triggering_env=tf_triggering_env,
            metric=metric_name,
        )

        branch_time_series_dict[ts_name] = {
            "labels": branch_tags.copy(),
            "data": {datapoints_timestamp: metric_value},
        }
    return True, branch_time_series_dict