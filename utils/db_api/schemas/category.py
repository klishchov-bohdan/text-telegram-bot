from sqlalchemy import Column, BigInteger, String, sql, Float

from utils.db_api.db_gino import TimedBaseModel


class Category(TimedBaseModel):
    __tablename__ = 'categories'
    category_name = Column(String(200), primary_key=True)

    query: sql.select
