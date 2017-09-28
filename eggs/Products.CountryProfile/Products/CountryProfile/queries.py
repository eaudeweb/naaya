# -*- coding: utf-8 -*-
"""A collection of commonly used queries

Please format SQL queries. For example use http://sqlformat.appspot.com/
"""

def get_country_code(dbconn, **kw):
    """ Get country code based on label_en """
    sql = u"SELECT CNT_CODE FROM COUNTRY WHERE CNT_LABEL_EN='%(label_en)s'" % kw
    records = dbconn.query(sql)
    if records:
        records = records[0]
    return records

def get_country_name(dbconn, **kw):
    """ Get the country name for a given code """
    sql = u"""
    SELECT cnt_label
    FROM COUNTRY
    WHERE cnt_code = '%(cnt)s'
    """ % kw
    records = dbconn.query(sql)
    if records:
        return records[0].get('cnt_label')

def get_source_value(dbconn, **kw):
    """ Get the source value for a given code """
    sql = u"""
    SELECT src_label
    FROM SOURCE
    WHERE src_code = '%(src)s'
    """ % kw
    records = dbconn.query(sql)
    if records:
        return records[0].get('src_label')

def get_indicator_value(dbconn, **kw):
    """ Get the indicator value for a given code """
    sql = u"""
    SELECT var_label 
    FROM VARIABLE
    WHERE var_code = '%(var)s'
    """ % kw
    records = dbconn.query(sql)
    if records:
        return records[0].get('var_label')

def get_table_data(dbconn, **kw):
    """ Returns a variable's value for the latest year for a given source and
    country

    """

    sql = u"""
    SELECT VARIABLE.var_label, VALUE.val, VARIABLE.var_unit, SOURCE.src_code,
                                                                VALUE.val_year
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN COUNTRY ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    WHERE VARIABLE.var_code = '%(var)s'
      AND COUNTRY.cnt_code = '%(cnt)s'
      AND SOURCE.src_code = '%(src)s'
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
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN COUNTRY ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    WHERE VARIABLE.var_code = '%(var)s'
        AND COUNTRY.cnt_code = '%(cnt)s'
        AND SOURCE.src_code = '%(src)s'
    ORDER BY VALUE.val_year
    """ % kw
    return dbconn.query(sql)

def get_indicators(dbconn, **kw):
    """ Returns the list of indicators that have content in the the VALUE table"""
    sql = u"""
    SELECT DISTINCT VARIABLE.var_code, VARIABLE.var_label
    FROM VARIABLE
    INNER JOIN VALUE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    ORDER BY VARIABLE.var_label
    """ % kw
    return dbconn.query(sql)

def get_available_sources(dbconn, **kw):
    """ Returns the list of sources for a given indicator """
    sql = u"""
    SELECT SOURCE.src_code, SOURCE.src_label
    FROM SOURCE
    INNER JOIN VARIABLE ON (VARIABLE.var_src_code = SOURCE.src_code)
    WHERE VARIABLE.var_code = '%(var)s'
    ORDER BY SOURCE.src_code
    """ % kw
    return dbconn.query(sql)

def get_available_years(dbconn, **kw):
    """ Returns the available years for a given indicator and source """
    sql = u"""
    SELECT DISTINCT VALUE.val_year
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    WHERE VARIABLE.var_code = '%(var)s'
    AND SOURCE.src_code = '%(src)s'
    ORDER BY VALUE.val_year
    """ % kw
    return dbconn.query(sql)

def get_available_countries(dbconn, **kw):
    """ Returns the available countries for a given indicator and source """
    sql = u"""
    SELECT DISTINCT COUNTRY.cnt_code, COUNTRY.cnt_label
    FROM COUNTRY
    INNER JOIN VALUE ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    WHERE VARIABLE.var_code = '%(var)s'
    AND SOURCE.src_code = '%(src)s'
    ORDER BY COUNTRY.cnt_code
    """ % kw
    return dbconn.query(sql)

def get_countries_by_sources(dbconn, **kw):
    """ Returns the available countries for a given indicator"""
    sql = u"""
    SELECT DISTINCT COUNTRY.cnt_code, COUNTRY.cnt_label
    FROM COUNTRY
    INNER JOIN VALUE ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    WHERE VARIABLE.var_code = '%(var)s'
    ORDER BY COUNTRY.cnt_code
    """ % kw
    return dbconn.query(sql)

def get_country_comparision(dbconn, **kw):
    """ Returns the country's indicator value for a given indicator, source and year"""
    sql = u"""
    SELECT VALUE.val, VALUE.val_cnt_code, COUNTRY.cnt_label
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN COUNTRY ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    WHERE VARIABLE.var_code = '%(var)s'
    AND VALUE.val_year = '%(year)s'
    AND SOURCE.src_code = '%(src)s'
    ORDER BY VALUE.val_cnt_code
    """ % kw
    return dbconn.query(sql)

def get_year_comparision(dbconn, **kw):
    """ Returns the year's indicator value for a given indicator, source and country"""
    sql = u"""
    SELECT VALUE.val, VALUE.val_year
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN COUNTRY ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    WHERE VARIABLE.var_code = '%(var)s'
    AND SOURCE.src_code = '%(src)s'
    AND COUNTRY.cnt_code = '%(cnt)s'
    ORDER BY VALUE.val_year
    """ % kw
    return dbconn.query(sql)

def get_source_comparision(dbconn, **kw):
    """ Returns the source's indicator value for a given indicator and country"""
    sql = u"""
    SELECT VALUE.val, VALUE.val_year, SOURCE.src_code 
    FROM VALUE
    INNER JOIN VARIABLE ON (VALUE.var_code = VARIABLE.var_code AND VALUE.val_src = VARIABLE.var_src_code)
    INNER JOIN SOURCE ON (VARIABLE.var_src_code = SOURCE.src_code)
    INNER JOIN COUNTRY ON (VALUE.val_cnt_code = COUNTRY.cnt_code)
    WHERE VARIABLE.var_code = '%(var)s'
    AND COUNTRY.cnt_code = '%(cnt)s'
    ORDER BY VALUE.val_year, SOURCE.src_code
    """ % kw
    return dbconn.query(sql)

def get_source_comparision_grouped(dbconn, **kw):
    """ Returns the source's indicator value for a given indicator and country groupped by year"""
    result = {}
    sources = []
    years = []

    for record in get_source_comparision(dbconn, **kw):
        result[(record['val_year'], record['src_code'])] = record['val']
        if record['src_code'] not in sources:
            sources.append(record['src_code'])
        if record['val_year'] not in years:
            years.append(record['val_year'])

    years.sort()
    sources.sort()
    return result, sources, years
