from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, \
                        MetaData
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.sql.expression import text

#Creating 3 tables. Records, a table for fulltext search fields, and
#one for normal key/values like date and language fields

metadata = MetaData()
tables = {}
tables['records_table'] = Table(
    'records',
    metadata,
    Column('id', String(100), primary_key=True),
    Column('harvester', String(200), index=True),
    Column('date_added', TIMESTAMP(), index=True,
           server_default=text("CURRENT_TIMESTAMP")),
    mysql_charset='utf8',
)
tables['records_map_table'] = Table(
    'records_map',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('record_id', String(100), ForeignKey('records.id')),
    Column('lang', String(2), index=True),
    Column('key', String(50), index=True),
    Column('value', String(1024), index=True),
    mysql_charset='utf8',
)
#Use it for dc_description, dc_title
tables['records_map_full_table'] = Table(
    'records_map_full',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('record_id', String(100), ForeignKey('records.id')),
    Column('lang', String(2), index=True),
    Column('key', String(50), index=True),
    Column('value', Text),
    mysql_charset='utf8',
)
