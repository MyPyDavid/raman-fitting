"""
Created on Thu Aug  5 10:01:32 2021

@author: DW
"""

import raman_fitting
from raman_fitting.indexing.indexer import MakeRamanFilesIndex


def export_to_db(self):
    """saves the index to a relational database"""

    from sqlalchemy import create_engine, inspect, select
    from sqlalchemy.schema import Table, Column, MetaData, ForeignKey
    from sqlalchemy.types import String, ARRAY, Float, BLOB, Integer, JSON
    from sqlalchemy.orm import declarative_base, relationship

    Base = declarative_base()

    class Ramanfiles(Base):
        __tablename__ = "ramanfiles"

        rfID = Column(String, primary_key=True)
        # children = relationship("RawSpectrum")

    class RawSpectrum(Base):
        __tablename__ = "rawspectrum"
        rfID = Column(String, ForeignKey("ramanfiles.rfID"), nullable=False)
        ramanshift = Column("ramanshift", JSON, nullable=True, primary_key=True)
        intensity = Column("intensity", JSON, nullable=True)
        # parent_id = Column(Integer, ForeignKey('parent.id'))
        # parent = relationship("Ramanfiles")
        # , back_populates="children")
        def __repr__(self):
            return f"{self.__class__.__qualname__} (rfID={self.rfID}, ramanshift ({len(self.ramanshift)}), intensity ({len(self.intensity)}))"

    #%%
    # df_to_db_sqlalchemy(self.DB_FILE, self.index, self.table_name, PathParser.index_primary_key)
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, inspect

    DB_name = f"sqlite:////{str(self.DB_FILE.absolute())}"
    engine = create_engine(DB_name, future=True)

    inspector = inspect(engine)
    Base.metadata.drop_all(engine)
    # Base.metadata.drop_all(engine, Ramanfiles, checkfirst=True)
    meta = MetaData()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    if self.pp_collection:
        for pp in self.pp_collection:
            if pp.data:
                pptable = pp
                rfID = pp.parse_result.get("rfID")
                tb_rfID = "tb_" + rfID

                ramanfile = Ramanfiles(**{"rfID": rfID})
                session.add(ramanfile)
                session.commit()
                # hash(list(pptable.data.ramanshift))
                spec = Table(
                    tb_rfID,
                    meta,
                    Column("id", String, foreign_key="ramanfiles.rfID"),
                    Column("index", Integer, primary_key=True),
                    Column("ramanshift", Float),
                    Column("intensity", Float),
                    extend_existing=True,
                )
                spec.create(engine)

                attr_dict = {
                    "__tablename__": tb_rfID,
                    "index": Column(Integer),
                    "ramanshift": Column(Float, primary_key=True),
                    "intensity": Column(Float),
                    "__table_args__": {"extend_existing": True},
                }

                MyTableClass = type(rfID, (Base,), attr_dict)

                for n, (_r, _int) in enumerate(
                    zip(pp.data.ramanshift, pp.data.intensity)
                ):

                    specrow = spec(index=n, ramanshift=_r, intensity=_int)
                    session.add(specrow)
                    spec.insert(index=n, ramanshift=_r, intensity=_int)
                session.commit()

                # specrow = RamanRawSpectrum(rfID=pp.parse_result.get('rfID'),
                #                  ramanshift = _r,
                #                  intensity = _int)
                # session.add(specrow)
    #%%

    # pp_db_rawspec = RamanRawSpectrum(rfID=pp.parse_result.get('rfID'),
    #                                  ramanshift=', '.join(map(str,pp.data.ramanshift)),
    #                                  intensity=', '.join(map(str,pp.data.intensity)))
    #                                  # ramanshift=pp.data.ramanshift,
    # intensity=pp.data.intensity)
    # pp_db_rawspec.__tablename__ = pp.parse_result.get('rfID')
    # session.add(pp_db_rawspec)
    # df_to_db_sqlalchemy(self.DB_FILE, pp.data.spectrum, self.table_name, PathParser.index_primary_key)
    session.commit()

    session.rollback()
    session.close()

    def select():
        statement = select(Ramanfiles).filter_by(
            rfID="e2e718bf932c42eede94b9246086d223_testDW38C_pos1"
        )
        result = session.execute(statement).all()


def db_schema():

    from sqlalchemy.schema import Table, Column, MetaData, ForeignKey
    from sqlalchemy.types import String, ARRAY, Float
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

    class RamanRawSpectrum(Base):
        __tablename__ = "raw_spectrum"

        rfID = Column(String, ForeignKey("parent.rfID"), nullable=False)
        ramanshift = Column("ramanshift", ARRAY(Float), nullable=True, primary_key=True)
        intensity = Column("intensity", ARRAY(Float), nullable=True)
        # parent_id = Column(Integer, ForeignKey('parent.id'))
        # parent = relationship("Ramanfiles", back_populates="children")

        def __repr__(self):
            return f"{self.__class__.__qualname__} (rfID={self.rfID}, ramanshift ({len(self.ramanshift)}), intensity ({len(self.intensity)}))"

    return None


def db_Table():
    metadata = MetaData()
    raman_spectrum_table = Table(
        "raw_spectrum",
        metadata,
        Column("rfID", String, ForeignKey("ramanfiles.rfID"), nullable=False),
        Column("ramanshift", ARRAY(Float), nullable=True),
        Column("intensity", ARRAY(Float), nullable=True),
    )
    return raman_spectrum_table


def main():
    RamanIndex = MakeRamanFilesIndex(run_mode="make_examples_index", read_data=True)
    expdb = export_to_db(RamanIndex)


if __name__ == "__main__":

    try:
        main()
    except Exception as exc:
        print(f"Main failed with exc: {exc}")


# def save_merge_to_db(self, DB_filepath, data, table_name, primary_key ):
#     df_to_db_sqlalchemy(DB_filepath, data, table_name, primary_key)
