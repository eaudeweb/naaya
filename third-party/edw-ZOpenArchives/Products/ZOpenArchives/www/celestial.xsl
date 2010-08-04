<?xml version="1.0" encoding="UTF-8"?>
<!--
Celestial OAI XSLT

Based to a large extent on OCLC's stylesheet & mechanism by Jeff Young

This stylesheet is provided under the same license as Celestial.

Copyright 2003 University of Southampton
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:oai="http://www.openarchives.org/OAI/2.0/" xmlns:oai_id="http://www.openarchives.org/OAI/2.0/oai-identifier" xmlns:oai_branding="http://www.openarchives.org/OAI/2.0/branding/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:oai_etdms="http://www.ndltd.org/standards/metadata/etdms/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:toolkit="http://oai.dlib.vt.edu/OAI/metadata/toolkit" xmlns:oai_provenance="http://www.openarchives.org/OAI/2.0/provenance" xmlns:oai_friends="http://www.openarchives.org/OAI/2.0/friends/">
	<xsl:output method="html" version="4.0"/>
	<xsl:template match="/oai:OAI-PMH">
		<html>
			<head>
				<title>
					<xsl:value-of select="oai:request/@verb"/> Response</title>
				<style type="text/css">
h1 {
	font-family: sans-serif;
	font-size: 170%;
}
h2 {
	font-family: sans-serif;
	font-size: 130%;
}
h3 {
	font-family: sans-serif;
	font-size: 120%;
}
h4 {
	font-family: sans-serif;
	font-size: 110%;
}
a {
	font-family: Verdana, Helvetica;
	font-size: 80%
}
p.list {
	text-decoration: underline;
}
.xml_tag {
	font-family: courier, monospace;
	color: darkred;
}
.xml_bracket {
	font-family: courier, monospace;
	color: blue;
}
.xml_value {
	font-family: Verdana, sans-serif;
	color: black;
	font-size: 80%;
}
.xml_attribute_name {
	font-family: courier, monospace;
	color: darkred;
}
.xml_attribute_value {
	font-family: courier, monospace;
	color: black;
}
table {
}
table.data {
	width: 100%;
	background: wheat;
	border: '2px groove gray';
	border-color: DimGray;
	border-width: 2px;
	border-style: solid;
}
table.xml {
	border-width: 0px;
}
td {
}
td.xml {
	border-width: 10px;
	margin: 0px;
}
td.name {
	width: 20%;
	background: lightyellow;
	border-color: gray;
	border-width: 1px;
	border-style: solid;
	font-family: sans-serif;
	font-size: smaller;
}
td.value {
	width: 80%;
	background: lightyellow;
	border-color: gray;
	border-width: 1px;
	border-style: solid;
}
</style>
			</head>
			<body>
				<table width="800px">
					<tr>
						<td>
							<a href="http://www.openarchives.org/">
								<img align="right" src="http://www.openarchives.org/images/OA100.gif" border="0"/>
							</a>
							<h1>OAI-PMH Response</h1>
							<p class="list">
								<a href="?verb=Identify">Identify</a> | <a href="?verb=ListIdentifiers&amp;metadataPrefix=oai_dc">ListIdentifiers</a> | <a href="?verb=ListMetadataFormats">ListMetadataFormats</a> | <a href="?verb=ListRecords&amp;metadataPrefix=oai_dc">ListRecords</a> | <a href="?verb=ListSets">ListSets</a>
							</p>
							<p>You are viewing this page because you are using a browser that supports XSLT (XML stylesheet transforms), and the repository has indicated this page is to be displayed using the <a href="http://celestial.eprints.org/">Celestial</a> XSL.</p>
							<table class="data">
								<tr>
									<td class="name">responseDate</td>
									<td class="value">
										<xsl:value-of select="oai:responseDate"/>
									</td>
								</tr>
								<tr>
									<td class="name">request</td>
									<td class="value">
										<xsl:apply-templates select="oai:request"/>
									</td>
								</tr>
							</table>
							<xsl:apply-templates select="oai:error|oai:GetRecord|oai:Identify|oai:ListIdentifiers|oai:ListMetadataFormats|oai:ListRecords|oai:ListSets"/>
						</td>
					</tr>
				</table>
				<p>Stylesheet written by Tim Brody, largely based on the stylesheet by Jeff Young at OCLC. Copyright 2003 University of Southampton. This stylesheet is released under the same license as Celestial (GPL). Neither Tim Brody, University of Southampton, or Jeff Young/OCLC are in any way responsible for the data exposed using this stylesheet.</p>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="oai:request">
		<xsl:value-of select="."/>?verb=<xsl:value-of select="@verb"/>
		<xsl:for-each select="@*">
			<xsl:if test="name() != 'verb'">&amp;<xsl:value-of select="name()"/>=<xsl:value-of select="."/>
			</xsl:if>
		</xsl:for-each>
	</xsl:template>
	<xsl:template match="oai:GetRecord">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The GetRecord verb provides a metadata (e.g. Dublin Core) record for an item.</p>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:Identify">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The Identify verb provides information about the OAI-compliant repository, e.g. collection-level rights and administrative contact details.</p>
		<table class="data">
			<xsl:apply-templates select="oai:adminEmail|oai:baseURL|oai:compression|oai:deletedRecord|oai:earliestDatestamp|oai:granularity|oai:protocolVersion|oai:repositoryName"/>
		</table>
		<xsl:apply-templates select="oai:description"/>
	</xsl:template>
	<xsl:template match="oai:ListIdentifiers">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The ListIdentifiers verb lists the items that can be disseminated in the requested metadata format.</p>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:ListMetadataFormats">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The ListMetadataFormats verb lists the metadata (e.g. Dublin Core) formats that can be disseminated for repository items.</p>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:ListRecords">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The ListRecords verb provides metadata (e.g. Dublin Core) records for items that can be disseminated for the requested format, and optionally set membership and date restriction.</p>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:ListSets">
		<h2>
			<xsl:value-of select="name()"/>
		</h2>
		<p>The ListSets verb lists the set hierarchy of the repository (if supported).</p>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:error">
		<h2>
			<xsl:value-of select="name()"/> - <xsl:value-of select="./@code"/>
		</h2>
		<p>
			<xsl:value-of select="."/>
		</p>
	</xsl:template>
	<xsl:template match="oai:adminEmail">
		<tr>
			<td class="name">Administrator's Email Address (adminEmail)</td>
			<td class="value">
				<a href="mailto:{.}">
					<xsl:value-of select="."/>
				</a>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:baseURL">
		<tr>
			<td class="name">Repository OAI Interface URL (baseURL)</td>
			<td class="value">
				<a href="{.}">
					<xsl:value-of select="."/>
				</a>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:compression">
		<tr>
			<td class="name">Supported HTTP Compression (compression)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:deletedRecord">
		<tr>
			<td class="name">Deleted Record Policy (deletedRecord)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:earliestDatestamp">
		<tr>
			<td class="name">Earliest Datestamp (earliestDatestamp)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:granularity">
		<tr>
			<td class="name">Finest Supported Granularity of Datestamps (granularity)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:protocolVersion">
		<tr>
			<td class="name">OAI Protocol Version (protocolVersion)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:repositoryName">
		<tr>
			<td class="name">Repository Name (repositoryName)</td>
			<td class="value">
				<xsl:value-of select="."/>
			</td>
		</tr>
	</xsl:template>
	<xsl:template match="oai:description">
		<h4>Description:
<xsl:for-each select="./*">
				<xsl:value-of select="name()"/>
			</xsl:for-each>
		</h4>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai_id:oai-identifier">
		<p>If an OAI repository uses OAI identifiers, the oai-identifier description provides information about the identifier space used by the repository.</p>
		<table class="data">
			<xsl:for-each select="./*">
				<tr>
					<td class="name">
						<xsl:value-of select="name()"/>
					</td>
					<td class="value">
						<xsl:value-of select="."/>
					</td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
	<xsl:template match="oai_friends:friends">
		<p>The friends description provides a list of OAI interface URLs of other repositories that are related in some way to the current repository.</p>
		<table class="data">
			<xsl:for-each select="./*">
				<tr>
					<td class="value">
						<a href="{.}">
							<xsl:value-of select="."/>
						</a>
					</td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
	<xsl:template match="oai:record">
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:header">
		<h4>Header: <a href="?verb=ListMetadataFormats&amp;identifier={./oai:identifier}">
				<xsl:value-of select="./oai:identifier"/>
			</a>
		</h4>
		<table class="data">
			<tr>
				<td class="name">datestamp</td>
				<td class="value">
					<xsl:value-of select="./oai:datestamp"/>
				</td>
			</tr>
			<xsl:for-each select="oai:setSpec">
				<tr>
					<td class="name">setSpec</td>
					<td class="value">
						<a href="?verb=ListIdentifiers&amp;metadataPrefix=oai_dc&amp;set={.}">
							<xsl:value-of select="."/>
						</a>
					</td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
	<xsl:template match="oai:metadata">
		<h4>Metadata</h4>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:about">
		<h4>About</h4>
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="oai:metadataFormat">
		<xsl:if test="/oai:OAI-PMH/oai:request/@identifier">
			<p>View this record in <a href="?verb=GetRecord&amp;metadataPrefix={./oai:metadataPrefix}&amp;identifier={/oai:OAI-PMH/oai:request/@identifier}">
					<xsl:value-of select="./oai:metadataPrefix"/>
				</a>.</p>
		</xsl:if>
		<table class="data">
			<tr>
				<td class="name">metadataPrefix</td>
				<td class="value">
					<a href="?verb=ListRecords&amp;metadataPrefix={./oai:metadataPrefix}">
						<xsl:value-of select="./oai:metadataPrefix"/>
					</a>
				</td>
			</tr>
			<tr>
				<td class="name">schema</td>
				<td class="value">
					<a href="{./oai:schema}">
						<xsl:value-of select="./oai:schema"/>
					</a>
				</td>
			</tr>
			<tr>
				<td class="name">metadataNamespace</td>
				<td class="value">
					<xsl:value-of select="./oai:metadataNamespace"/>
				</td>
			</tr>
		</table>
	</xsl:template>
	<xsl:template match="oai:resumptionToken">
		<p>
			<table class="data" style="background: lightgreen">
				<tr>
					<td class="name" style="background: white">resumptionToken</td>
					<td class="value" style="background: white">
						<a href="?verb={/oai:OAI-PMH/oai:request/@verb}&amp;resumptionToken={.}">
							<xsl:value-of select="."/>
						</a>
					</td>
				</tr>
				<xsl:for-each select="@*">
					<tr>
						<td class="name" style="background: white">
							<xsl:value-of select="name()"/>
						</td>
						<td>
							<xsl:value-of select="."/>
						</td>
					</tr>
				</xsl:for-each>
			</table>
		</p>
	</xsl:template>
	<xsl:template match="oai:set">
		<table class="data">
			<tr>
				<td class="name">setSpec</td>
				<td class="value">
					<a href="?verb=ListRecords&amp;metadataPrefix=oai_dc&amp;set={./oai:setSpec}">
						<xsl:value-of select="./oai:setSpec"/>
					</a>
				</td>
			</tr>
			<tr>
				<td class="name">setName</td>
				<td class="value">
					<xsl:value-of select="./oai:setName"/>
				</td>
			</tr>
			<xsl:apply-templates select="oai:description"/>
		</table>
	</xsl:template>
	<xsl:template match="oai_dc:dc">
		<table class="data">
			<tr>
				<td class="name">oai_dc</td>
				<td class="value">
					<a href="http://www.openarchives.org/OAI/2.0/oai_dc.xsd">http://www.openarchives.org/OAI/2.0/oai_dc.xsd</a>
				</td>
			</tr>
			<xsl:for-each select="./*">
				<tr>
					<td class="name">
						<xsl:value-of select="name()"/>
					</td>
					<td class="value">
						<xsl:value-of select="."/>
					</td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
	<xsl:template match="oai_provenance:provenance">
		<p>Record was harvested at <xsl:value-of select="./oai_provenance:originDescription/@harvestDate"/> and is <xsl:if test="./oai_provenance:originDescription/@altered = 'false'">unaltered</xsl:if>
			<xsl:if test="./oai_provenance:originDescription/@altered != 'false'">altered</xsl:if> by the OAI cache/proxy.</p>
		<table class="data">
			<xsl:for-each select="./oai_provenance:originDescription/*">
				<tr>
					<td class="name">
						<xsl:value-of select="name()"/>
					</td>
					<td class="value">
						<xsl:value-of select="."/>
					</td>
				</tr>
			</xsl:for-each>
		</table>
	</xsl:template>
	<xsl:template name="raw">
		<table style="margin-left: 10px" cellspacing="0" cellpadding="0" class="xml">
			<tr>
				<td class="xml">
					<span class="xml_bracket">&lt;<span class="xml_tag">
							<xsl:value-of select="name()"/>
						</span>
						<xsl:for-each select="@*">
							<xsl:text> </xsl:text>
							<span class="xml_attribute_name">
								<xsl:value-of select="name()"/>
							</span>="<span class="xml_attribute_value">
								<xsl:value-of select="."/>
							</span>"</xsl:for-each>&gt;</span>
					<xsl:if test="count(./*)">
						<xsl:for-each select="./*">
							<xsl:call-template name="raw"/>
						</xsl:for-each>
					</xsl:if>
					<xsl:if test="count(./*)=0">
						<span class="xml_value">
							<xsl:value-of select="."/>
						</span>
					</xsl:if>
					<span class="xml_bracket">&lt;/<span class="xml_tag">
							<xsl:value-of select="name()"/>
						</span>&gt;</span>
				</td>
			</tr>
		</table>
	</xsl:template>
	<xsl:template match="*">
		<table class="data">
			<tr>
				<td class="value">
					<xsl:call-template name="raw"/>
				</td>
			</tr>
		</table>
	</xsl:template>
</xsl:stylesheet>