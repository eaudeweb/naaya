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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
import os
from OracleConnector import OracleConnector, manage_addOracleConnectorForm, manage_addOracleConnector
from App.ImageFile import ImageFile



def initialize(context):
    """ Initialize the OracleConnector product"""
    os.environ['ORACLE_HOME'] = '/u01/app/oracle/product/9.2.0.1.0'
    os.environ['LD_LIBRARY_PATH'] = ':/u01/app/oracle/product/9.2.0.1.0/lib:/u01/app/oracle/product/9.2.0.1.0/network/lib'
    context.registerClass(
        OracleConnector,
        constructors = (manage_addOracleConnectorForm, manage_addOracleConnector),
        permission = 'Add OracleConnector',
        icon = 'www/OracleConnector.gif'
    )
