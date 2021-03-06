import csv
import re

from redisbench_admin.utils.local import check_if_needs_remote_fetch


def prepare_tsbs_run_queries_redistimeseries_benchmark_command(
    executable_path: str,
    server_private_ip: object,
    server_plaintext_port: object,
    benchmark_config: object,
    current_workdir,
    result_file: str,
    remote_queries_file,
):
    """
    Prepares tsbs_run_queries_redistimeseries command parameters
    :param executable_path:
    :param server_private_ip:
    :param server_plaintext_port:
    :param benchmark_config:
    :param current_workdir:
    :return: [string] containing the required command to run the benchmark given the configurations
    """
    command_arr = [executable_path]

    command_arr.extend(
        ["--host", "{}:{}".format(server_private_ip, server_plaintext_port)]
    )

    for k in benchmark_config["parameters"]:
        if "workers" in k:
            command_arr.extend(["--workers", str(k["workers"])])
        if "max-queries" in k:
            command_arr.extend(["--max-queries", str(k["max-queries"])])
        if "file" in k:
            input_file = k["file"]
            input_file = check_if_needs_remote_fetch(
                input_file, "/tmp", None, remote_queries_file
            )
            command_arr.extend(["--file", input_file])

    command_arr.extend(["--results-file", result_file])
    command_arr.extend(["--print-interval", "1000"])

    command_str = " ".join(command_arr)
    return command_arr, command_str


def post_process_ycsb_results(stdout, start_time_ms, start_time_str):
    results_dict = {
        "Tests": {},
        "StartTime": start_time_ms,
        "StartTimeHuman": start_time_str,
    }
    if type(stdout) == bytes:
        stdout = stdout.decode("ascii")
    csv_data = list(csv.reader(stdout.splitlines(), delimiter=","))
    start_row = 0
    for row in csv_data:
        if len(row) >= 1:
            if "[OVERALL]" in row[0]:
                break
        start_row = start_row + 1
    for row in csv_data[start_row:]:
        if len(row) >= 3:
            op_group = row[0].strip()[1:-1]
            metric_name = row[1].strip()
            metric_name = re.sub("[^0-9a-zA-Z]+", "_", metric_name)
            value = row[2].strip()
            if op_group not in results_dict["Tests"]:
                results_dict["Tests"][op_group] = {}
            results_dict["Tests"][op_group][metric_name] = value
    return results_dict
