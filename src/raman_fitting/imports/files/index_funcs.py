import logging
import sys

from pathlib import Path

from raman_fitting.imports.spectrum.datafile_parsers import load_dataset_from_file

logger = logging.getLogger(__name__)


def get_dtypes_filepath(index_file):
    _dtypes_filepath = index_file.with_name(
        index_file.stem + "_dtypes" + index_file.suffix
    )
    return _dtypes_filepath


def export_index(index, index_file):
    """saves the index to a defined Index file"""
    if index.empty:
        logger.info(f"{__name__} Empty index not exported")
        return

    if not index_file.parent.exists():
        logger.info(f"{__name__} created parent dir: {index_file.parent}")
        index_file.parent.mkdir(exist_ok=True, parents=True)

    index.to_csv(index_file)

    _dtypes = index.dtypes.to_frame("dtypes")
    _dtypes.to_csv(get_dtypes_filepath(index_file))

    logger.info(
        f"{__name__} Succesfully Exported Raman Index file to:\n\t{index_file}\nwith len({len(index)})."
    )


def load_index(index_file, reload=False):
    """loads the index from from defined Index file"""
    if not index_file.exists() or reload:
        logger.error(
            f"Error in load_index: {index_file} does not exists, starting reload index ... "
        )
        return
        # index = make_index()
        # export_index(index, index_file)
        # return index
    # breakpoint()

    try:
        _dtypes = load_dataset_from_file(
            get_dtypes_filepath(index_file), index_col=[0]
        ).to_dict()["dtypes"]

        _dtypes_datetime = {
            k: val
            for k, val in _dtypes.items()
            if "datetime" in val or k.endswith("Date")
        }

        _dtypes_no_datetime = {
            k: val for k, val in _dtypes.items() if k not in _dtypes_datetime.keys()
        }

        index = load_dataset_from_file(
            index_file,
            index_col=[0],
            dtype=_dtypes_no_datetime,
            parse_dates=list(_dtypes_datetime.keys()),
        )
        # index = _extra_assign_destdir_and_set_paths(index)

        logger.info(
            f"Succesfully imported Raman Index file from {index_file}, with len({len(index)})"
        )
        if not len(index) == len(index):
            logger.error(
                f"""'Error in load_index from {index_file},
                            \nlength of loaded index not same as number of raman files
                            \n starting reload index ... """
            )
            # index = make_index()
            # return index

    except Exception as e:
        logger.error(
            f"Error in load_index from {index_file},\n{e}\n starting reload index ... "
        )


def index_selection(index, **kwargs):
    """
    Special selector on the index DataFrame

    Parameters
    -------

    index
        pd.DataFrame containing the index of files
        should contains columns that are given in index_file_sample_cols and index_file_stat_cols
    default_selection str
        all or '' for empty default
    kwargs
        checks for keywords suchs as samplegroups, sampleIDs, extra
        meant for cli commands

    Returns
    -------
    index_selection
        pd.DataFrame with a selection from the given input parameter index
        default returns empty DataFrame

    """
    if index is None:
        return

    if not kwargs:
        return index

    default_selection = kwargs.get("default_selection", "all")
    if "normal" not in kwargs.get("run_mode", default_selection):
        default_selection = "all"
    index_selection = None  # pd.DataFrame()
    logger.info(
        f"starting index selection from index({len(index)}) with:\n default selection: {default_selection}\n and {kwargs}"
    )

    if not index:
        logger.warning("index selection index arg empty")
        return

    if default_selection:
        if default_selection == "all":
            index_selection = index.copy()

    if "samplegroups" in kwargs:
        if kwargs["samplegroups"]:
            index = list(
                filter(lambda x: x.sample.group in kwargs["samplegroups"], index)
            )
            # index_selection = index.loc[
            #     index.SampleGroup.str.contains("|".join(kwargs["samplegroups"]))
            # ]
    if "sampleIDs" in kwargs:
        index = list(filter(lambda x: x.sample.id in kwargs["sampleIDs"], index))
        # index_selection = index.loc[
        #     index.SampleID.str.contains("|".join(kwargs["sampleIDs"]))
        # ]

    if "extra" in kwargs:
        runq = kwargs.get("run")
        if "recent" in runq:
            grp = index.sort_values(
                "FileCreationDate", ascending=False
            ).FileCreationDate.unique()[0]

            index_selection = index.loc[index.FileCreationDate == grp]
            index_selection = index_selection.assign(
                **{
                    "DestDir": [
                        Path(i).joinpath(grp.strftime("%Y-%m-%d"))
                        for i in index_selection.DestDir.values
                    ]
                }
            )

    # if "make_examples" in run_mode:
    #     index_selection = index.loc[~index.SampleID.str.startswith("Si")]

    logger.debug(
        f"finished index selection from index({len(index)}) with:\n {default_selection}\n and {kwargs}\n selection len({len(index_selection )})"
    )

    if not index_selection:
        logger.warning("index selection empty. exiting")
        sys.exit()

    return index_selection


def test_positions(sample_group_files):
    if not sample_group_files:
        return

    _files = [i.file for i in sample_group_files]
    _positions = [i.sample.position for i in sample_group_files]
    if len(set(_files)) != len(set(_positions)):
        logger.warning(
            f"{sample_group_files[0].sample} Unique files and positions not matching for {sample_group_files}"
        )
    return sample_group_files
