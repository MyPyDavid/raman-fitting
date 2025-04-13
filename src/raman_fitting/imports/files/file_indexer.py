# """Indexer for raman data files"""
#
# from loguru import logger
# from raman_fitting.config import settings
# from raman_fitting.imports.files.collectors import collect_raman_file_index_info
# from raman_fitting.imports.files.index.models import RamanFileIndex
#
# from raman_fitting.imports.files.selectors import select_index
#
#
# def main():
#     """test run for indexer"""
#     index_file = settings.destination_dir.joinpath("index.csv")
#     raman_files = collect_raman_file_index_info()
#     try:
#         index_data = {"file": index_file, "raman_files": raman_files}
#         raman_index = RamanFileIndex(**index_data)
#         logger.debug(f"Raman Index len: {len(raman_index.dataset)}")
#         select_index(raman_index.raman_files, sample_groups=["DW"], sample_ids=["DW38"])
#     except Exception as e:
#         logger.error(f"Raman Index error: {e}")
#         raman_index = None
#
#     return raman_index
#
# if __name__ == "__main__":
#     main()
