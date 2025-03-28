from pydantic import BaseModel


class Sch_Upload_Audio(BaseModel):
    filename: str
    path: str
