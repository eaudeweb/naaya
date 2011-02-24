# -*- coding: utf-8 -*-
"""A collection of commonly used queries

Please format SQL queries. For example use http://sqlformat.appspot.com/
"""

def get_table_data(dbconn, **kw):
    """ Returns a variable's value for the latest year for a given source and
    country

    """

    sql = u"""
    SELECT VARIABLE.var_label, VALUE.val, VARIABLE.var_unit, SOURCE.src_label,
                                                                VALUE.val_year
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN country ON (VALUE.val_cnt_code = country.cnt_code)
    WHERE VARIABLE.var_code = '%(variable)s'
      AND country.cnt_code = '%(country)s'
      AND SOURCE.src_code = '%(source)s'
    ORDER BY VALUE.val_year DESC LIMIT 1
    """ % kw
    records = dbconn.query(sql)
    if records:
        records = records[0]
    return records

def get_chart_data(dbconn, **kw):
    """ Returns the evolution overtime for a given variable, source and country

    """

    sql = u"""
    SELECT VARIABLE.var_label, VALUE.val, VARIABLE.var_unit, SOURCE.src_code,
                                                            VALUE.val_year
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN country ON (VALUE.val_cnt_code = country.cnt_code)
    WHERE VARIABLE.var_code = '%(variable)s'
        AND country.cnt_code = '%(country)s'
        AND SOURCE.src_code = '%(source)s'
    ORDER BY VALUE.val_year
    """ % kw
    return dbconn.query(sql)
