naaya.semide

=== Description

This is a custom setup of Naaya for SEMIDE network. It contains custom content
types which can be found in naaya/content/semide. SEMIDESite is the custom
layer on top of Naaya.

=== Instalation

SEMIDE requires a few libraries for pdf generation: pyfribidi and a custom version
of reportlab (custom because it was required to be modified to suport RTL languages)
After installing the above dependencies it should be easy to install using
zc.buildout

=== Changes

22-04-2010 - Alexandru Plugaru

    Ported all SEMIDE to Zope 2.10 and latest Naaya
	Switched to Naaya Schema Tool for all content types

13-01-2006 - Dragos

	MODIFICATIONS
		- se creaza 2 remote channels in fiecare tara:
			* 1 pt "Legislation on Water"
			* 1 pt "Project water"
			QUESTION: cum vom baga in cron canalele astea?
		- se creeaza index custom pt project_water
		- legislation_water folder cu index customizat

	UPDATE:
		- crearea/update la index project_water
		- update legislation_water folder + index
		- crearea canalelor daca nu exista
		- update portlet_country_left
		- update forme la country
		- delete country_legislationwater page


16-01-2006 - Alex

	UPDATE:
		- update la forma folder_index
		- update la forma site_search
