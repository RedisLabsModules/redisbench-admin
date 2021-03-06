import yaml

from redisbench_admin.run.ycsb.ycsb import (
    prepare_ycsb_benchmark_command,
    post_process_ycsb_results,
)


def test_prepare_ycsbbenchmark_command():
    with open("./tests/test_data/ycsb-config.yml", "r") as yml_file:
        benchmark_config = yaml.safe_load(yml_file)
        for k in benchmark_config["clientconfig"]:
            if "parameters" in k:
                command_arr, command_str = prepare_ycsb_benchmark_command(
                    "ycsb", "localhost", "6380", k, "/root"
                )
                assert (
                    command_str
                    == 'ycsb load redisearch -P /root/workloads/workload-ecommerce -p "threadcount=64"'
                    ' -p "redis.host=localhost" -p "redis.port=6380"'
                    " -p dictfile=/root/bin/uci_online_retail.csv"
                    " -p recordcount=100000 -p operationcount=100000"
                )

                command_arr, command_str = prepare_ycsb_benchmark_command(
                    "ycsb", "localhost", "6380", k, None
                )
                assert (
                    command_str
                    == 'ycsb load redisearch -P ./workloads/workload-ecommerce -p "threadcount=64"'
                    ' -p "redis.host=localhost" -p "redis.port=6380"'
                    " -p dictfile=./bin/uci_online_retail.csv"
                    " -p recordcount=100000 -p operationcount=100000"
                )


def test_post_process_ycsb_results():
    input = b'[DEBUG]  YCSB home: /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT\n[DEBUG]  YCSB home: /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT\n/usr/bin/java -cp /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/redisearch-binding/conf:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/conf:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/javatuples-1.2.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/cache-api-1.0.0.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/slf4j-api-1.7.25.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/log4j-core-2.11.0.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/log4j-to-slf4j-2.11.2.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/generex-1.0.2.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/HdrHistogram-2.1.4.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/javafaker-1.0.2.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/ignite-shmem-1.0.0.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/jackson-core-asl-1.9.4.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/core-0.18.0-SNAPSHOT.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/log4j-api-2.11.2.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/ignite-log4j2-2.7.6.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/annotations-13.0.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/htrace-core4-4.1.0-incubating.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/snakeyaml-1.23-android.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/commons-pool2-2.9.0.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/redisearch-binding-0.18.0-SNAPSHOT.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/automaton-1.11-8.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/commons-lang3-3.5.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/jackson-mapper-asl-1.9.4.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/ignite-core-2.7.6.jar:/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/lib/jedis-3.5.2.jar site.ycsb.Client -db site.ycsb.db.RediSearchClient -P /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/workloads/workload-ecommerce -p "threadcount=64" -p "redis.host=localhost" -p "redis.port=6379" -p dictfile=/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/bin/uci_online_retail.csv -p recordcount=100000 -p operationcount=100000 -load\nCommand line: -db site.ycsb.db.RediSearchClient -P /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/workloads/workload-ecommerce -p "threadcount=64" -p "redis.host=localhost" -p "redis.port=6379" -p dictfile=/home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/bin/uci_online_retail.csv -p recordcount=100000 -p operationcount=100000 -load\nYCSB Client 0.18.0-SNAPSHOT\n\nLoading workload...\nLoading search dictionary (property=\'dictfile\') from: /home/fco/redislabs/RediSearch/tests/ci.benchmarks/binaries/ycsb-redisearch-binding-0.18.0-SNAPSHOT/bin/uci_online_retail.csv\nRead 100000\nRead 200000\nRead 300000\nRead 400000\nRead 500000\nRead 600000\nRead 700000\nRead 800000\nRead 900000\nRead 1000000\nusing a dictionary of 1067370 to generate productName and search terms\nStarting test.\nSLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".\nSLF4J: Defaulting to no-operation (NOP) logger implementation\nSLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.\nDBWrapper: report latency for each error is false and specific error codes to track for latency are: []\n[OVERALL], RunTime(ms), 24564\n[OVERALL], Throughput(ops/sec), 4070.998208760788\n[TOTAL_GCS_G1_Young_Generation], Count, 23\n[TOTAL_GC_TIME_G1_Young_Generation], Time(ms), 279\n[TOTAL_GC_TIME_%_G1_Young_Generation], Time(%), 1.13580850024426\n[TOTAL_GCS_G1_Old_Generation], Count, 0\n[TOTAL_GC_TIME_G1_Old_Generation], Time(ms), 0\n[TOTAL_GC_TIME_%_G1_Old_Generation], Time(%), 0.0\n[TOTAL_GCs], Count, 23\n[TOTAL_GC_TIME], Time(ms), 279\n[TOTAL_GC_TIME_%], Time(%), 1.13580850024426\n[CLEANUP], Operations, 1\n[CLEANUP], AverageLatency(us), 1592.0\n[CLEANUP], MinLatency(us), 1592\n[CLEANUP], MaxLatency(us), 1592\n[CLEANUP], 95thPercentileLatency(us), 1592\n[CLEANUP], 99thPercentileLatency(us), 1592\n[INSERT], Operations, 100000\n[INSERT], AverageLatency(us), 86.16328\n[INSERT], MinLatency(us), 39\n[INSERT], MaxLatency(us), 6555\n[INSERT], 95thPercentileLatency(us), 147\n[INSERT], 99thPercentileLatency(us), 224\n[INSERT], Return=OK, 100000\n'
    results_dict = post_process_ycsb_results(input.decode("ascii"), None, None)
    assert "INSERT" in results_dict["Tests"]
    assert results_dict["Tests"]["INSERT"]["95thPercentileLatency_us_"] == "147"
