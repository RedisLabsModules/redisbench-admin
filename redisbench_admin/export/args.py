def create_export_arguments(parser):
    parser.add_argument('--benchmark-result-files', type=str, required=True,
                        help="benchmark results files to read results from. can be a local file, a remote link, or an s3 bucket.")
    parser.add_argument('--steps', type=str, default="setup,benchmark",
                        help="comma separated list of steps to be analyzed given the benchmark result files")
    parser.add_argument('--exporter', type=str, default="csv",
                        help="exporter to be used ( either csv or redistimeseries )")
    return parser