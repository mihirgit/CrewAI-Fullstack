from pydantic import BaseModel
from typing import List


class NamedUrl(BaseModel):
    name: str
    url: str


class PositionInfo(BaseModel):
    company: str
    position: str
    name: str
    blog_articles_url: List[str]
    youtube_interview_url: List[NamedUrl]


class PositionInfoList(BaseModel):
    positions: List[PositionInfo]
