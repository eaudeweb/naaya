1) How to add a custom search for a country under
'Countries Environmental Information' ... 'Projets de Recherche':

Create a public interface on that specific folder and add this code to it:

<tal:block replace="structure python:here.country_search(here, 'COUNTRY_NAME')" />

where COUNTRY_NAME is the full country name, e.g. France


2) How to add a custom search for a country under
'Countries Environmental Information' ... 'Experts':

Create a public interface on that specific folder and add this code to it:

<tal:block replace="structure python:here.country_search_experts(here, 'COUNTRY_NAME')" />

where COUNTRY_NAME is the full country name, e.g. France