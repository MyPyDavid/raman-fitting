from pydantic import BaseModel


class SampleMetaData(BaseModel):
    id: str
    group: str
    position: int = 0
