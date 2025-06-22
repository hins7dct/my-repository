from pydantic import BaseModel


class SingleShortUrlCreate(BaseModel):
    """
    创建短链记录时需要传递的参数信息
    """
    long_url: str
    short_url: str = "http://127.0.0.1:8000/"
    visits_count: int = 0
    short_tag: str = ""
    created_by: str = ""
