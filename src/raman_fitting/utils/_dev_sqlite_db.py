"""Generate the default sqlite database.
reference: pygaps
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


# class DBError
def df_to_db_sqlalchemy(
    DB_filepath, data, table_name: str, primary_key: str, merge_columns=[]
):
    """
    Parameters
    ----------
    DB_filepath : pathlike path or str
        path to database file, used to create engine
    data : pd.DataFrame
        DataFrame which will be stored in the database
    table_name : str
        name of the table on which the DataFrame will be stored

    merge_column : list of str
        name of the column on which the DataFrames will be merged


    Returns
    -------
    None.

    """

    from sqlalchemy import create_engine

    if False:  # FIXME for testing
        table_name = "raman_files"
        primary_key = "FilePath"

    DB_name = f"sqlite:////{str(DB_filepath.absolute())}"

    engine = create_engine(DB_name)
    DB_table_names = engine.table_names()

    if table_name in DB_table_names:
        # Checking for values of FilePath
        df_read = pd.read_sql(table_name, engine)
        # drop new index column for read_sql, else it will keep adding columns
        if "index" in df_read.columns:
            df_read.drop(columns=["index"], inplace=True)

        df_read_FP_uniq = set()
        data_FP_uniq = set()

        if hasattr(df_read, primary_key) and hasattr(data, primary_key):
            df_read_FP_uniq = set(df_read[primary_key].unique())
            data_FP_uniq = set(data[primary_key].unique())

        FP_union = df_read_FP_uniq | data_FP_uniq
        if data_FP_uniq != df_read_FP_uniq:

            # if data_FP_uniq > df_read_FP_uniq:
            #
            data = convert_object_columns_to_string(data)
            # automatic merge columns
            _mcols = set(data.columns) & set(df_read.columns)

            if merge_columns:
                _mcols = merge_columns

            _merged_data = pd.merge(data, df_read, on=list(_mcols), how="outer")

            _merged_data.to_sql(
                table_name, con=engine, if_exists="replace", index=False
            )

    else:  # TODO
        data = convert_object_columns_to_string(data)
        data.to_sql(table_name, con=engine, index=False)
        # data.to_sql(table_name, con=engine, if_exists='replace')


def convert_object_columns_to_string(DF: pd.DataFrame):
    DF = DF.assign(**{i: DF[i].apply(str) for i in DF.columns if DF[i].dtype == "O"})
    return DF


def _dev_db_extra():
    import sqlite3
    import raman_fitting
    import json

    # from pygaps.parsing import sqlite as pgsqlite
    pgsqlite = None
    from raman_fitting.utils.exceptions import DataBaseError
    from raman_fitting.utils._todo_sqlite_db_pragmas import PRAGMAS

    def db_create(pth, verbose=False):
        """
        Create the entire database.
        Parameters
        ----------
        pth : str
            Path where the database is created.
        """
        for pragma in PRAGMAS:
            db_execute_general(pragma, pth, verbose=verbose)

        # Get json files
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            # Try backported to PY<37 `importlib_resources`.
            import importlib_resources as pkg_resources

        # Get and upload adsorbate property types
        ads_props_json = None
        # pkg_resources.read_text(
        #     'pygaps.data', 'adsorbate_props.json'
        # )
        ads_props = json.loads(ads_props_json)
        for ap_type in ads_props:
            pgsqlite.adsorbate_property_type_to_db(
                ap_type, db_path=pth, verbose=verbose
            )

        # Get and upload adsorbates
        ads_json = None
        # pkg_resources.read_text('pygaps.data', 'adsorbates.json')
        adsorbates = json.loads(ads_json)
        for ads in adsorbates:
            pass
            # pgsqlite.adsorbate_to_db(
            #     pygaps.Adsorbate(**ads), db_path=pth, verbose=verbose
            # )

        # Upload standard isotherm types
        pgsqlite.isotherm_type_to_db({"type": "isotherm"}, db_path=pth)
        pgsqlite.isotherm_type_to_db({"type": "pointisotherm"}, db_path=pth)
        pgsqlite.isotherm_type_to_db({"type": "modelisotherm"}, db_path=pth)

    def db_execute_general(statement, pth, verbose=False):
        """
        Execute general SQL statements.
        Parameters
        ----------
        statement : str
            SQL statement to execute.
        pth : str
            Path where the database is located.
        """
        # Attempt to connect
        try:
            # TODO remove str call on python 3.7
            with sqlite3.connect(str(pth)) as db:

                # Get a cursor object
                cursor = db.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")

                # Check if table does not exist and create it
                cursor.executescript(statement)

        # Catch the exception
        except sqlite3.Error as e_info:
            logger.info(f"Unable to execute statement: \n{statement}")
            raise DataBaseError from e_info
