from sqlalchemy import Column, BigInteger, String, sql, Float

from utils.db_api.db_gino import TimedBaseModel


class File(TimedBaseModel):
    __tablename__ = 'files'
    file_id = Column(String, primary_key=True)
    file_name = Column(String(200))
    file_category = Column(String(50))
    file_description = Column(String(500))

    query: sql.select