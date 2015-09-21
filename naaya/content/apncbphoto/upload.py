import xlrd
from alchemy import get_or_create, session
from alchemy import Author, Image, Park, Biome, Vegetation, Document
import datetime

AUTHOR_NAME_COL = 0
AUTHOR_CODE_COL = 1
IMAGE_CODE_COL = 2
IMAGE_ID_COL = 3
IMAGE_FORMAT_COL = 4
IMAGE_FORM_COL = 5
IMAGE_STOCK_COL = 6
SUBJECT_COL = 7
PARK_CODE_COL = 8
TOPIC_COL = 9
REF_GEO_COL = 10
NO_COLLECTION_COL = 11
SUJET_BREF_COL = 12
ESP_NOM_COM_COL = 13
ESP_NOM_LAT_COL = 14
BIOME_NAME_COL = 15
VEGETATION_NAME_COL = 16
PAYSAGE_COL = 17
BATIMENT_COL = 18
PERSONNE_COL = 19
ALTITUDE_COL = 20
DATE_COL = 21
REFERENCE_COL = 22
REF_ID_LOCAL_COL = 23
LONGITUDE_COL = 24
LATITUDE_COL = 25

ALLOW_SHOW_COLUMN = (0, 2, 7, 8, 9, 15, 16, 20, 21, 24, 25)


def process_workbook(workbook):
    tworkbook = []
    for sheet in workbook.sheets():
        tsheet = []
        if sheet.nrows > 1:
            for row in range(1, sheet.nrows):
                trow = [row]
                for column in range(sheet.ncols):
                    if column in ALLOW_SHOW_COLUMN:
                        elem = sheet.cell(row, column).value
                        tval = elem
                        if column == DATE_COL:
                            if elem:
                                try:
                                    tval = datetime.datetime(
                                        *xlrd.xldate_as_tuple(elem,
                                                              workbook.datemode
                                                              )).date()
                                except ValueError:
                                    tval = elem
                                except TypeError:
                                    tval = elem
                        elif type(elem) is unicode:
                            tval = elem.encode('utf-8', 'replace')
                        trow.append(tval)
                tsheet.append(trow)
        tworkbook.append(tsheet)
    return tworkbook


def create_sheet_matrix(sheet, workbook):
    matrix = [[0 for x in range(sheet.ncols)] for x in range(sheet.nrows)]
    for row in range(1, sheet.nrows):  # exclude the first row
        for column in range(sheet.ncols):
            elem = sheet.cell(row, column).value
            if column == DATE_COL:
                if elem:
                    try:
                        matrix[row-1][column] = datetime.datetime(
                            *xlrd.xldate_as_tuple(elem,
                                                  workbook.datemode)).date()
                    except ValueError:
                        matrix[row-1][column] = elem
                    except TypeError:
                        matrix[row-1][column] = elem
                else:
                    matrix[row-1][column] = ''
                continue
            if type(elem) is unicode:
                matrix[row-1][column] = elem.encode('utf-8', 'replace')
            else:
                matrix[row-1][column] = elem
    return matrix


def save_uploaded_file(workbook):

    for sheet in workbook.sheets():
        matrix = create_sheet_matrix(sheet, workbook)
        for row in range(len(matrix)):
            author_name = matrix[row][AUTHOR_NAME_COL] if matrix[row][
                AUTHOR_NAME_COL] else 'undefined'
            author_code = matrix[row][AUTHOR_CODE_COL] if matrix[row][
                AUTHOR_CODE_COL] else 'undefined'
            author = get_or_create(session, Author,
                                   name=author_name,
                                   code=author_code
                                   )
            image = get_or_create(session, Image,
                                  code=str(
                                      matrix[row][IMAGE_CODE_COL]).lower(),
                                  id=matrix[row][IMAGE_ID_COL],
                                  format=matrix[row][IMAGE_FORMAT_COL],
                                  form=matrix[row][IMAGE_FORM_COL],
                                  stock=matrix[row][IMAGE_STOCK_COL]
                                  )
            park_code = matrix[row][PARK_CODE_COL] if matrix[row][
                PARK_CODE_COL] else 'undefined'
            park = get_or_create(session, Park, code=park_code)
            biome = get_or_create(session, Biome, name=matrix[row][
                BIOME_NAME_COL])
            vegetation = get_or_create(
                session, Vegetation, name=matrix[row][VEGETATION_NAME_COL])
            document = Document(
                authorid=author.authorid,
                imageid=image.imageid,
                subject=matrix[row][SUBJECT_COL],
                parkid=park.parkid,
                topic=matrix[row][TOPIC_COL],
                ref_geo=matrix[row][REF_GEO_COL],
                no_collection=matrix[row][NO_COLLECTION_COL],
                sujet_bref=matrix[row][SUJET_BREF_COL],
                esp_nom_com=matrix[row][ESP_NOM_COM_COL],
                esp_nom_lat=matrix[row][ESP_NOM_LAT_COL],
                biomeid=biome.biomeid,
                vegetationid=vegetation.vegetationid,
                paysage=matrix[row][PAYSAGE_COL],
                batiment=matrix[row][BATIMENT_COL],
                personne=matrix[row][PERSONNE_COL],
                date=matrix[row][DATE_COL],
                reference=matrix[row][REFERENCE_COL],
                ref_id_local=matrix[row][REF_ID_LOCAL_COL],
                altitude=matrix[row][ALTITUDE_COL],
                longitude=matrix[row][LONGITUDE_COL],
                latitude=matrix[row][LATITUDE_COL],
            )
            session.add(document)
            session.commit()
    return process_workbook(workbook)
