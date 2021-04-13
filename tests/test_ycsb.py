import yaml

from redisbench_admin.run.ycsb.ycsb import prepareYCSBBenchmarkCommand


#
# def test_ensure_ycsb_on_path():
#     directory_to = tempfile.mkdtemp()
#     ensure_ycsb_on_path("ycsb",
#                         "https://s3.amazonaws.com/benchmarks.redislabs/redisearch/ycsb/ycsb-redisearch-binding-0.18.0-SNAPSHOT.tar.gz",
#                         directory_to)


def test_prepare_ycsbbenchmark_command():
    with open("./tests/test_data/ycsb-config.yml", "r") as yml_file:
        benchmark_config = yaml.safe_load(yml_file)
        for k in benchmark_config["clientconfig"]:
            if 'parameters' in k:
                command_arr, command_str = prepareYCSBBenchmarkCommand("ycsb", "localhost", "6380", k)
                assert command_str == "ycsb load redisearch -P workloads/workload-ecommerce -p \"threadcount=64\"" \
                                      " -p \"redis.host=localhost\" -p \"redis.port=6380\"" \
                                      " -p \"recordcount=100000\" -p \"operationcount=100000\""
