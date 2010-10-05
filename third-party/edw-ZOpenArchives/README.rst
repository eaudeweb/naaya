edw-ZOpenArchives
=================
Zope2 management of OAI2

Description
-----------
This is a Zope2 Product that uses OAI2 protocol to harverst and provide OAI2 data.
It consists of 2 main Products, `OAI Server` and `OAI Aggregator`.
Both contain harversters. An OAI Harverster has remote or local data sources
and generates OAI Records for an OAI Repository (Aggregator or Server).


OAI Server stores it's OAI Record's in a ZCatalog generated from local site
meta types such a news items through OAI Harvester's. There is a web api (see
OAI2 server protocol) that publishes these local records for sharing with others.


OAI Aggregator gets it's data from remote OAI2 providers and can store the
harversted data into a storage type. Currentlly OAI Aggregator supports ZCatalog
and SQLAlchemy storage types. The harvested records can be searched via a web
interface inside the portal. The recommended storage type is SQLAlchemy because
of the nature of the data structure of the OAI.


Both the OAI Server and OAI Aggregator must be updated using cron.


This product is build upon pyoai package of http://www.infrae.com/download/OAI/pyoai
Please refer to http://www.openarchives.org/OAI/openarchivesprotocol.html for protocol reference.

Here is simplified structure the product:

 - OAI Repository (common wrapper for Aggregator and Server)
    - OAI Aggregator
       - OAI Harvester (gets remote records from OAI servers)
       - OAI Namespace (use to store DublinCore data)
       - OAI Tokens (used for resumptionToken storage)
       - OAI Record's
    - OAI Server - provides
       - OAI Harvester (harvests localy from ZCatalog)
       - OAI Record's

Usage
-----
A common use case for product usage.

OAI Aggregator
++++++++++++++

After adding an OAI Aggregator (from ZMI) and providing the preffered data
storage, to gather the remote servers' records an OAI Harverster must be added
to the OAI Aggregator.
After the OAI Harversters are setup the harverting settings can be refined using OAI Sets.
Also an manual update can be triggered using the Update tab in ZMI (if there
are a lot of OAI records this can take a while).
After the update process is finished the new OAI Records can be searched via a web:

http://path_to_site/oai/search_form
This form can be found in zpt/search_form.zpt

OAI Server
++++++++++

After adding an OAI Server (from ZMI), local OAI Harvesters must be setup to
gather local meta types (one per line in Meta types). The same process of update
applies to the OAI Server.

The server API URL is:

http://path_to_site/zoai/
