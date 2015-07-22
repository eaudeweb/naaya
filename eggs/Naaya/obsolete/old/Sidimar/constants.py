# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports

#Product imports
import Globals

SIDIMAR_PRODUCT_NAME = 'Sidimar'
SIDIMAR_PRODUCT_PATH = Globals.package_home(globals())

USERSTOOL_ID = 'acl_users'
USERSTOOL_TITLE = 'User folder'
USERSTOOL_METATYPE = 'Sidimar User Folder'

MYSQLTOOL_ID = 'mysql'
MYSQLTOOL_TITLE = 'MySQL manager'
MYSQLTOOL_METATYPE = 'Sidimar MySQL manager'


PERMISSION_ADD_SIDIMARSITE = 'Sidimar - Add Sidimar Site objects'

METATYPE_SIDIMARSITE = 'Sidimar Site'

ERROR100 = 'Name required'
ERROR101 = 'Lastname required'
ERROR102 = 'Country required'
ERROR103 = 'Street required'
ERROR104 = 'Street number required'
ERROR105 = 'Zip required'
ERROR106 = 'City required'
ERROR107 = 'Region required'
ERROR108 = 'Phone required'
ERROR109 = 'Email required'
ERROR110 = 'Condizioni di utilizzo required'
ERROR111 = 'Informativa sulla privacy required'
ERROR112 = """I'm sorry. We do not have record of your email. 
            Please ensure that you are entering the proper email and try again. 
            If you continue to have problems, contact customer service at:"""

ERROR115 = 'Old password must be specified'
ERROR116 = 'Invalid password. Please insert the corect password.'
ERROR117 = 'Password and confirmation do not match'
ERROR118 = 'Password and confirmation must be specified'
ERROR119 = 'An user with the specified name already exists'
ERROR120 = 'No user selected'
ERROR121 = 'You must specify an username'
ERROR122 = 'You must specify a password'
MESSAGE_SAVEDCHANGES = 'Saved changes %s'

LOG_ACTIVATE_USER = "Activate user %s"
LOG_DEACTIVATE_USER = "Deactivate user %s"
LOG_CREATE_USER = "Create user %s"
LOG_UPDATE_USER = "Update credentials for %s"
LOG_DELETE_USER = "Delete user %s"

LOG_CHG_CRED = "Change credentials"
LOG_CHG_PASS = "Change password"

#download
FORNIT = "Fornitore"
COD = "Codice"
DESCR = "Descrizione"
UNIT = "Unita' Misura"
NAME = "Nome Strumento"
RIL = "Limite Rilevabilita'"

STAZ_DESCR = 'FORNITORE'
STAZ = 'STAZ'
LATG = 'LATG'
LATP = 'LATP'
LATS = 'LATS'
LATPC = 'LATPC'
LONGG = 'LONGG'
LONGP = 'LONGP'
LONGS = 'LONGS'
LONGPC = 'LONGPC'
CODISTAT = 'CODISTAT'
PROF_TOT = 'PROF_TOT'
DESCR = 'DESCRIZIONE'

STAZIONE = 'Stazione'
REGIONE = 'Regione'
DATA = 'Data'
MONITOR = 'Monitoraggio'
CAMPAG = 'Campagna'
DIST_SUP = 'Distanza Superfice'
PROGR_PREL = 'Progressivo'
COD_PARAM = 'Codparam'
NOME_SPECIE = 'Nome specie'
VALUE = 'Valore'

#graphic constants
TEMP = "C020"
SALINITA = "C031"
OXYGEN = "C080"
PH = "C100"
CLOROFILLA = "C114"

SEDIMENTI_METAL_CODES = [
    'SAL2', #Alluminio
    'DAS2', #Arsenico
    'DCD2', #Cadmio
    'DCR2', #Cromo
    'SFE2', #Ferro
    'DCU2', #Rame
    'DHG2', #Mercurio
    'DNI2', #Nichelio
    'DPB2', #Piombo
    'DVV2', #Vanadio
    'DZN2', #Zinco
    'DC02'  #Carbonio organico
]
SEDIMENTI_TRIBUTILSTAGNO_CODE = 'S04T' #Tributilstagno
SEDIMENTI_COMPOSTIORGANOCLORURATI = [
    'S080', #Idrocarburi clorurati
    'S081', #4-4` DDT Diclorodifeniltricloroetano
    'S082', #2-4` DDT Diclorodifeniltricloroetano
    'S083', #4-4` DDE Diclorodifeniletilene
    'S084', #2-4` DDE Diclorodifeniletano
    'S085', #4-4` DDD Diclorodifenildicloroetano
    'S086', #2-4` DDD
    'S087', #DD^S totali
    'S088', #alfa HCH Esaclorocicloesano
    'S089', #beta HCH Esaclorocicloesano
    'S08A', #gamma  HCH Esaclorocicloesano
    'S08B', #delta HCH Esaclorocicloesano
    'S08C', #Aldrin
    'S08D', #Dieldrin
    'S08E', #Esaclorobenzene
    'S08Q', #Eptacloro+eptacloroeposido
    'S08R', #Endrine
    'S08S', #Endosulfat
    'S08T'  #Metossicloro
]
SEDIMENTI_POLICLOROBIFENILI_CODE = [
    'S091', #Policlorobifenili 52 (4 - Cl)
    'S092', #Policlorobifenili 77 (4 - Cl)
    'S093', #Policlorobifenili 81 (4 - Cl)
    'S094', #Policlorobifenili 128 (6 - Cl)
    'S095', #Policlorobifenili 138 (6 - Cl)
    'S096', #Policlorobifenili 153 (6 - Cl)
    'S097'  #Policlorobifenili 169 (6 - Cl)
]
SEDIMENTI_IDROCARBURI_CODE = [
    'S044', #Acenaftilene
    'S045', #Acenaftene
    'S046', #Fluorene
    'S047', #Fenantrene
    'S048', #Antracene
    'S049', #Pirene
    'S04B', #Benzo `a` antracene
    'S04C', #Benzo `b` fluorantene
    'S04D', #Benzo `a` pirene
    'S04E', #Indeno `1-2-3 cd` pirene
    'S04F', #Dibenzo `a-h` antracene
    'S04G', #Benzo `g-h-i` perilene
    'S04H', #Fluorantene
    'S04J', #Benzo `k` fluorantene
    'S04L', #Crisene
    'S04M', #Idrocarburi policiclici aromatici
    'S04N', #Naftalene
    'S04O', #Acenaftilene
    'S04P'  #Fluorene
]
SEDIMENTI_SPORECLOSTRIDISOLFITORIDUTTORI_CODE = 'S100' #Spore clostridi solfitoriduttori
SEDIMENTI_GRANULOMETRIA_CODE = [
    'SPEL', #Peliti (diametro < 0.063 mm)
    'SSAB', #Sabbia (0.0063 mm < x < 2 mm)
    'SGHI'  #Ghiaia (diametro > 2 mm)
]


MOLLUSCHI_METAL_CODES = [
    'DAL1', #Alluminio
    'DAS1', #Arsenico
    'DCD1', #Cadmio
    'DCR1', #Cromo
    'DFE1', #Ferro
    'DCU1', #Rame
    'DHG1', #Mercurio
    'DNI1', #Nichelio
    'DPB1', #Piombo
    'DVV1', #Vanadio
    'DZN1'  #Zinco
]
MOLLUSCHI_TRIBUTILSTAGNO_CODE = 'I04T' #Tributilstagno
MOLLUSCHI_COMPOSTIORGANOCLORURATI = [
    'I080', #Idrocarburi clorurati
    'I081', #4-4` DDT Diclorodifeniltricloroetano
    'I082', #2-4` DDT Diclorodifeniltricloroetano (a)
    'I083', #4-4` DDE Diclorodifeniletilene
    'I084', #2-4` DDE Diclorodifeniletano (a)
    'I085', #4-4` DDD Diclorodifenildicloroetano
    'I086', #2-4` DDD (a)
    'I087', #DDD`s totali
    'I088', #alfa HCH Esaclorocicloesano (a)
    'I089', #beta HCH Esaclorocicloesano (b)
    'I08A', #gamma HCH Esaclorocicloesano (c)
    'I08B', #delta HCH Esaclorocicloesano (d)
    'I08C', #Aldrin
    'I08D', #Dieldrin
    'I08E', #Esaclorobenzene
]
MOLLUSCHI_POLICLOROBIFENILI_CODE = [
    'I091', #Policlorobifenili 52 (4 - CL)
    'I092', #Policlorobifenili 77 (4 - Cl)
    'I093', #Policlorobifenili 81 (4 - Cl)
    'I094', #Policlorobifenili 128 (6 - Cl)
    'I095', #Policlorobifenili 138 (6 - Cl)
    'I096', #Policlorobifenili 153 (6 - Cl)
    'I097'  #Policlorobifenili 169 (6 - Cl)
]
MOLLUSCHI_IDROCARBURI_CODE = [
    'I141', #Naftalene
    'I142', #Acenaftene
    'I143', #Acenaftilene
    'I144', #Fluorene
    'I145', #Fenantrene
    'I146', #Antracene
    'I147', #Fluorantene
    'I148', #Pirene
    'I149', #Benzo `a` antracene
    'I14A', #Crisene
    'I14B', #Benzo `b` fluorantene
    'I14C', #Benzo `k` fluorantene
    'I14D', #Benzo `a` pirene
    'I14E', #Indeno `1-2-3 cd` pirene
    'I14F', #Dibenzo `a-h` antracene
    'I14G' #Benzo `g-h-i` perilene
]

FITOPLANCTON_CODES = [
    'G021', #Diatomee
    'G022', #Dinoflagellate
    'G023'  #Altro fitoplancton
]

ZOOPLANCTON_CODES = [
    'G032',
    'G033',
    'G034'
]

W_MONIT_CODES = ['C020', 'C031', 'C060', 'C080', 'C100', 'C114', 'E010', 'E020', 'E030', 'E031', 'E040', 'E060', 'E070']
W_MONIT_CODES_VALUES = {'C020':'', 'C031':'', 'C060':'', 'C080':'', 'C100':'', 'C114':'', 'E010':'', 'E020':'', 'E030':'', 
                    'E031':'', 'E040':'', 'E060':'', 'E070':''}

Z_MONIT_CODES = ['DAL1', 'DAS1', 'DCD1', 'DCR1', 'DCU1', 'DFE1', 'DHG1', 'DNI1', 'DPB1', 'DVV1', 'DZN1', 'I04T', \
                'I081', 'I082', 'I083', 'I084', 'I085', 'I086', 'I087', 'I088', 'I089', 'I08A', 'I08B', 'I08C', \
                'I08D', 'I08E', 'I091', 'I092', 'I093', 'I094', 'I095', 'I096', 'I097', 'I098', 'I141', 'I142', \
                'I143', 'I144', 'I145', 'I146', 'I147', 'I148', 'I149', 'I14A', 'I14B', 'I14C', 'I14D', 'I14E', 'I14F', 'I14G']
Z_MONIT_CODES_VALUES = {'DAL1':'', 'DAS1':'', 'DCD1':'', 'DCR1':'', 'DCU1':'', 'DFE1':'', 'DHG1':'', 'DNI1':'', \
                'DPB1':'', 'DVV1':'', 'DZN1':'', 'I04T':'', 'I081':'', 'I082':'', 'I083':'', 'I084':'', 'I085':'', \
                'I086':'', 'I087':'', 'I088':'', 'I089':'', 'I08A':'', 'I08B':'', 'I08C':'', 'I08D':'', 'I08E':'', \
                'I091':'', 'I092':'', 'I093':'', 'I094':'', 'I095':'', 'I096':'', 'I097':'', 'I098':'', 'I141':'', \
                'I142':'', 'I143':'', 'I144':'', 'I145':'', 'I146':'', 'I147':'', 'I148':'', 'I149':'', 'I14A':'', \
                'I14B':'', 'I14C':'', 'I14D':'', 'I14E':'', 'I14F':'', 'I14G':''}

#X_MONIT_CODES = ['P010', 'P011', 'P012', 'P013', 'P014', 'P015', 'P016', 'P017', 'P018', 'P019', 'P020', 'P021', \
#                'P022', 'P023', 'P024', 'P025', 'P026', 'P027', 'P028', 'P029', 'P030', 'P040', 'P041', 'P042', \
#                'P050', 'P051', 'P052', 'P053', 'P054', 'P055', 'P060', 'P061', 'P062', 'P063', 'P064', 'P065', \
#                'P066', 'P067', 'P068', 'P069', 'SF10', 'SF20', 'SF30', 'SF40', 'SF50', 'SF60']
X_MONIT_CODES = ['SF10', 'SF20', 'SF30', 'SF40', 'SF50', 'SF60']

X_MONIT_CODES_VALUES = {'P010':'', 'P011':'', 'P012':'', 'P013':'', 'P014':'', 'P015':'', 'P016':'', 'P017':'', \
                 'P018':'', 'P019':'', 'P020':'', 'P021':'', 'P022':'', 'P023':'', 'P024':'', 'P025':'', 'P026':'', \
                 'P027':'', 'P028':'', 'P029':'', 'P030':'', 'P040':'', 'P041':'', 'P042':'', 'P050':'', 'P051':'', \
                 'P052':'', 'P053':'', 'P054':'', 'P055':'', 'P060':'', 'P061':'', 'P062':'', 'P063':'', 'P064':'', \
                 'P065':'', 'P066':'', 'P067':'', 'P068':'', 'P069':'', 'SF10':'', 'SF20':'', 'SF30':'', 'SF40':'', \
                 'SF50':'', 'SF60':''}

P_MONIT_CODES = ['G021', 'G022', 'G023', 'G032', 'G033', 'G034']
P_MONIT_CODES_VALUES = {'G021':'', 'G022':'', 'G023':'', 'G032':'', 'G033':'', 'G034':''}

S_MONIT_CODES = ['DAS2', 'DC02', 'DCD2', 'DCR2', 'DCU2', 'DHG2', 'DNI2', 'DPB2', 'DVV2', 'DZN2', 'S045', 'S047', 'S048', \
                'S049', 'S04B', 'S04C', 'S04D', 'S04E', 'S04F', 'S04G', 'S04H', 'S04J', 'S04L', 'S04M', 'S04N', 'S04O', \
                'S04P', 'S04T', 'S080', 'S081', 'S082', 'S083', 'S084', 'S085', 'S086', 'S087', 'S088', 'S089', 'S08A', \
                'S08B', 'S08C', 'S08D', 'S08E', 'S091', 'S092', 'S093', 'S094', 'S095', 'S096', 'S097', 'S098', 'S100', \
                'S101', 'S107', 'S108', 'S112', 'S113', 'S114', 'S115', 'S116', 'S117', 'S118', 'S119', 'S120', 'S121', \
                'S122', 'S123', 'SAL2', 'SFE2', 'SGHI', 'SPEL', 'SSAB']
S_MONIT_CODES_VALUES = {'DAS2':'', 'DC02':'', 'DCD2':'', 'DCR2':'', 'DCU2':'', 'DHG2':'', 'DNI2':'', 'DPB2':'', 'DVV2':'', \
                'DZN2':'', 'S045':'', 'S047':'', 'S048':'', 'S049':'', 'S04B':'', 'S04C':'', 'S04D':'', 'S04E':'', 'S04F':'', \
                'S04G':'', 'S04H':'', 'S04J':'', 'S04L':'', 'S04M':'', 'S04N':'', 'S04O':'', 'S04P':'', 'S04T':'', 'S080':'', \
                'S081':'', 'S082':'', 'S083':'', 'S084':'', 'S085':'', 'S086':'', 'S087':'', 'S088':'', 'S089':'', 'S08A':'', \
                'S08B':'', 'S08C':'', 'S08D':'', 'S08E':'', 'S091':'', 'S092':'', 'S093':'', 'S094':'', 'S095':'', 'S096':'', \
                'S097':'', 'S098':'', 'S100':'', 'S101':'', 'S107':'', 'S108':'', 'S112':'', 'S113':'', 'S114':'', 'S115':'', \
                'S116':'', 'S117':'', 'S118':'', 'S119':'', 'S120':'', 'S121':'', 'S122':'', 'S123':'', 'SAL2':'', 'SFE2':'', \
                'SGHI':'', 'SPEL':'', 'SSAB':''}