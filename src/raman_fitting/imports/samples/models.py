from pydantic import BaseModel


class SampleMetaData(BaseModel):
    id: str
    group: str
    position: int = 0

    model_config = {"frozen": True}
