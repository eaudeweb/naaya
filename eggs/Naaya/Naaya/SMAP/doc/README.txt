How to add a custom search for a country under
'Countries Environmental Information' ... ' Projets de Recherche':

Create a public interface on that specific folder and add this code to it:

<tal:block replace="structure python:here.country_search(here, 'COUNTY_NAME')" />

e.g. COUNTY_NAME -> France
