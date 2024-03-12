
declare -a args=(
    "--interface hdf5 --parallel_file_mode MIF 8"
    "--interface hdf5 --parallel_file_mode SIF 1"
    "--interface hdf5 --parallel_file_mode MIF 8 --part_size 10M"
    "--interface hdf5 --avg_num_parts 8 --part_size 100K --parallel_file_mode MIF 32"
    "--interface hdf5 --avg_num_parts 8 --part_size 10K --parallel_file_mode MIF 32"
    "--interface hdf5 --avg_num_parts 8 --part_size 1K --parallel_file_mode MIF 32"
)
