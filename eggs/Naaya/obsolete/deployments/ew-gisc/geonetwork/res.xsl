<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:include href="main.xsl"/>
	
	<!--
	html page
	-->
	<xsl:template match="/">
		<html>
			<head>
				<title><xsl:apply-templates select="/" mode="title"/></title>
				<link rel="stylesheet" type="text/css" href="{/root/gui/url}/geonetwork.css"/>
			</head>
			<body>
				<table width="100%" height="100%">
					<div id="container" style="">
						<div id="toolribbon">
							<div id="left_topnav">
							    <ul>
								<li><a href="http://www.ew.eea.europa.eu" title="EnviroWindows">EnviroWindows</a></li>
								<li><a href="http://www.eea.europa.eu" id="eealink">EEA</a></li>
								<li><a href="http://www.eionet.europa.eu">Eionet</a></li>
								<li><a href="http://www.gmes.info">GMES</a></li>
							    </ul>
							</div>
						</div>
						<div id="header">
							<a href="http://gmes.info/"><img class="leftfl" src="http://gisc.ew.eea.europa.eu/portal_layout/logo_en.gif" title="GMES" alt="GMES"></img></a>
							<a href="http://www.eea.europa.eu/"><img class="rightfl" src="http://gisc.ew.eea.europa.eu/portal_layout/envirowindows/EW-skin-13/logo-eea"></img></a>
							<a href="http://cordis.europa.eu/fp7/home_en.html"><img class="rightfl" src="http://gisc.ew.eea.europa.eu/portal_layout/envirowindows/EW-skin-13/logo-fp7"></img></a>
							<div class="page_title">GISC Catalogue</div>
						</div>
						<div id="menunav">
						</div>
						<div id="breadcrumbtrail">
							<a title="EnviroWindows" href="http://ew.eea.europa.eu">EW</a>
							 »
							<a href="http://gisc.ew.eea.europa.eu/" title="Home">Home</a>
							 »
							<a href="http://gisc.ew.eea.europa.eu/geonetwork/" title="Geonetwork">Geonetwork</a>
						</div>
					</div>
        			<tr height="100%">
						<td class="content" colspan="3">
							<xsl:call-template name="formLayout">
								<xsl:with-param name="title">
									<h1><xsl:apply-templates select="/" mode="title"/></h1>
								</xsl:with-param>
								<xsl:with-param name="content">
									<xsl:call-template name="content"/>
								</xsl:with-param>
							</xsl:call-template>
						</td>
        			
        				<!--
						<td class="padded-content" colspan="3">
							<h1><xsl:apply-templates select="/" mode="title"/></h1>
							<xsl:call-template name="content"/>
						</td>
						-->
        			</tr>
        		</table>
			</body>
		</html>
	</xsl:template>
	
	<!--
	title
	-->
	<xsl:template mode="title" match="/">
		<xsl:value-of select="/root/gui/strings/title"/>
	</xsl:template>
	
</xsl:stylesheet>
