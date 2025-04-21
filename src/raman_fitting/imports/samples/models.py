from pydantic import BaseModel


class SampleMetaData(BaseModel):
    id: str
    group: str
    position: int = 0

    model_config = {"frozen": True}

    def __lt__(self, other):
        if not isinstance(other, SampleMetaData):
            return NotImplemented
        return (self.group, self.id, self.position) < (
            other.group,
            other.id,
            other.position,
        )

    def __eq__(self, other):
        if not isinstance(other, SampleMetaData):
            return NotImplemented
        return (self.group, self.id, self.position) == (
            other.group,
            other.id,
            other.position,
        )

    def __str__(self):
        return f"SampleMetaData(id={self.id}, group={self.group}, position={self.position})"

    def __repr__(self):
        return self.__str__()
