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
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

#Form fields / select lists
form_names=['title', 'short_name', 'summary', 'web_link', 'contact_name', 'contact_organisation',
    'contact_email', 'analytical_technique_text', 'structure_text', 'developer_owner', 'history',
    'target', 'calibration', 'validation', 'uncertainty', 'key_reference', 'accessibility',
    'restrictions', 'links', 'participative_processes', 'other_comments']
form_text_areas=['summary', 'structure_text']
form_lists=['themes_covered', 'key_drivers', 'key_indicators', 'model_coverage', 'model_resolution',
    'model_time_horizon', 'model_time_steps', 'dominant_analytical_techniques']
comment_names=['author', 'body']


#Content of the select lists ("available")
potential_themes = ['Agriculture','Air', 'Biodiversity', 'Climate', 'Demography', 'Economy', 'Energy',
    'Human health', 'Forest', 'Fisheries', 'Integrated', 'Land use', 'Tourism', 'Transport',
    'Waste and material flows', 'Water']
potential_coverage = ['Global', 'EU-27', 'EU-15', 'EU-12', 'EU-10', 'Albania', 'Austria', '...', 'Sweden']
potential_resolution = ['Groups of countries', 'Countries (NUTS 0)', 'Provinces (NUTS 1)', 'Regions (NUTS 2)',
    'Counties (NUTS 3)', 'River basin level']
potential_time_horizon = ['2010s', '2020s', '2030s', '2040s', '2050s', '2100s']
potential_time_steps = ['Final year only', 'Every 10 years', 'Every 5 years', 'Every year', 'Every month', 'Every day']
accessibility_levels = ['Accessibility levels - please select', 'Very high', 'High', 'Limited', 'Very limited']

#Content of the sublists of the 'special' optgroup select list
equilibrium_models = ['general equilibrium models', 'partial equilibrium models or sectoral models',
    'mass balance equation models', 'optimisation models']
empirical_statistical_model = ['rule-based models', 'cellular automata', 'agent-based models',
    'multiple regression models', 'area-based matrix approaches', 'stochastic approaches', 'econometric models']
dynamic_system_model = ['linear/non-linear programming models', 'population dynamics models',
    'impact assessment models', 'integrated assessment models']
interactive_models = ['expert judgement frameworks', 'decision support systems', 'educational gaming', 'information tools']
# The 'special' grouped select list is defined as a list of tuples of lists
analytical_techniques = [('Equilibrium models',equilibrium_models), ('Empirical-statistical model',empirical_statistical_model), ('Dynamic system model',dynamic_system_model), ('Interactive models',interactive_models)]

#Mandatory fields in different forms
mandatory_fields_model = ['title', 'summary', 'contact_name', 'contact_organisation', 'contact_email']
mandatory_fields_comment = ['author', 'body']
mandatory_fields_authentication = ['authentication_email', 'authentication_password']

#Searchable fields
searchable_fields = ['title', 'short_name', 'summary', 'contact_name', 'contact_organisation', 'contact_email', 'body']
searchable_lists = ['dominant_analytical_techniques', 'themes_covered']

#Permissions
MANAGE_FACTSHEET = "OMI Manage Factsheet"
MANAGE_FACTSHEET_FOLDER = "OMI Manage Factsheet Folder"
ADD_FACTSHEET_FOLDER = "OMI Add Factsheet Folder"
ADD_FACTSHEET = "View"
ADD_FACTSHEET_COMMENT = "View"

#Mailhost object
MAILHOST = 'MailHost'

#Configuration init for ZTinyMCE
ZTinyMCE_CONFIGURATION = """
language : "en",
mode : "textareas",
theme : "advanced",
plugins : "directionality, fullscreen, paste, preview",
theme_advanced_buttons1: "bold, italic, underline, strikethrough, separator, justifyleft, justifycenter, justifyright, justifyfull, separator, bullist, numlist, separator, link, unlink, hr, removeformat, sub, sup, pastetext, pasteword, separator, preview, fullscreen, code",
theme_advanced_buttons2: "",
theme_advanced_buttons3 : "",
theme_advanced_toolbar_location : "top",
theme_advanced_toolbar_align : "left",
theme_advanced_path_location : "bottom",
plugin_insertdate_dateFormat : "%Y-%m-%d",
plugin_insertdate_timeFormat : "%H:%M:%S",
extended_valid_elements : "hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
theme_advanced_blockformats : "p,div,h2,h3,h4,h5,h6,blockquote",
theme_advanced_resize_horizontal : false,
theme_advanced_resizing : true
"""

#Template for assigning password
ASSIGN_PASSWORD_TEMPLATE = """\
<html>
    <head/>
    <body>
        <p>
            Hello,
        <p/>
        <p>
            You have created the following model in the "Online Management Inventory":
        <p/>
        <p>
            <a href="%(model_view_link)s">%(model_view_link)s</a>
        <p/>
        <p>
            You can edit this model by authenticating yourself with your email address and the password <strong>%(password)s</strong> at the following address:
        <p/>
        <p>
            <a href="%(model_edit_link)s">%(model_edit_link)s</a>
        <p/>
        <p>
            ---
        <p/>
        <p>
            If you believe you are using the correct information and cannot edit the model, report the problem at <a href="mailto:%(administrator_email)s">%(administrator_email)s</a>.<br/>
            This is an automatic message. Replies to this message will not be read or responded to.
        </p>
        <p>
            ---
        </p>
        <p>
            Best Regards,<br/>
            Online Management Inventory team
        </p>
    </body>
</html>"""

ASSIGN_PASSWORD_TEMPLATE_TEXT = """Hello, 

You have created the following model in the "Online Management Inventory":

%(model_view_link)s

You can edit this model by authenticating yourself with your email address and the password

%(password)s

at the following address:

%(model_edit_link)s

---
If you believe you are using the correct information and cannot edit the model, report the problem at %(administrator_email)s.
This is an automatic message. Replies to this message will not be read or responded to.
---

Best Regards,
Online Management Inventory team"""

#Template for administrative allert
MODEL_ADD_EDIT_TEMPLATE = """\
<html>
    <head/>
    <body>
        <p>
            Hello,
        <p/>
        <p>
            The following model was created / edited in the "Online Management Inventory":
        <p/>
        <p>
            <a href="%(model_view_link)s">%(model_view_link)s</a>
        <p/>
        <p>
            You are registered as the administrator of this folder.
        </p>
        <p>
            ---
        </p>
        <p>
            Best Regards,<br/>
            Online Management Inventory team
        </p>
    </body>
</html>"""

MODEL_ADD_EDIT_TEMPLATE_TEXT = """Hello, 

This email is registered as the administrative address for the "Online Management Inventory".

The following model was created / edited in the "Online Management Inventory":

%(model_view_link)s

You are registered as the administrator of this folder.

---
Best Regards,
Online Management Inventory team"""

#Template for comment notification
MODEL_ADD_COMMENT_TEMPLATE = """\
<html>
    <head/>
    <body>
        <p>
            Hello,
        <p/>
        <p>
            A comment was added by <strong>%(comment_author)s</strong> in the "Online Management Inventory" for the following model:
        <p/>
        <p>
            <a href="%(model_view_link)s">%(model_view_link)s</a>
        <p/>
        <p>
            ---
        </p>
        <p>
            Best Regards,<br/>
            Online Management Inventory team
        </p>
    </body>
</html>"""

MODEL_ADD_COMMENT_TEMPLATE_TEXT = """Hello, 

A comment was added by %(comment_author)s in the "Online Management Inventory" for the following model:

%(model_view_link)s

---
Best Regards,
Online Management Inventory team"""

#Template for administrative allert
FOLDER_ADD_EDIT_TEMPLATE = """\
<html>
    <head/>
    <body>
        <p>
            Hello,
        <p/>
        <p>
            The following factsheet folder was created / edited in the "Online Management Inventory":
        <p/>
        <p>
            <a href="%(folder_view_link)s">%(folder_view_link)s</a>
        <p/>
        <p>
            You are registered as the administrator of this folder.
        </p>
        <p>
            ---
        </p>
        <p>
            Best Regards,<br/>
            Online Management Inventory team
        </p>
    </body>
</html>"""

FOLDER_ADD_EDIT_TEMPLATE_TEXT = """Hello, 

The following factsheet folder was created / edited in the "Online Management Inventory":

%(folder_view_link)s

You are registered as the administrator of this folder.

---
Best Regards,
Online Management Inventory team"""

