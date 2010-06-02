# -*- coding: iso-8859-15 -*-


#################
# DEPRECATED
#################

import string
# file with helpful XML/DOM methods

class MyXMLLib:
    """ """

    def getDOMElementText(self, dom_node=None, encode=None):
        """
        input is a DOM node

        returns text of node; encoded text if
          encode parameter is given
        """
        text = ""
        for node in dom_node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text = text + string.strip(node.data)
        if encode != None:
            text = text.encode(encode)
        return text.strip()

    def findDOMElements(self, dom_list=[], tag_path=[]):
        """
        finds DOM elements in DOM trees by path
        path is a list of strings - eg, [ 'Adressbook','Adress','Person','Name']
        which corresponds to tag names in XML
        returns list of nodes which have this path, or [] for none
        """
        found_nodes = []
        if len(dom_list)==0 or len(tag_path)==0:
            return found_nodes

        # get next tag to search for
        tag_name = tag_path[0]
        new_path = tag_path[1:]
        for dom in dom_list:
##            for node in dom.getElementsByTagName(tag_name):
##                found_nodes.append(node)
            for node in dom.childNodes:
                if hasattr(node, 'tagName') and node.tagName == tag_name:
                    found_nodes.append(node)

        if len(new_path):
            found_nodes = self.findDOMElements(dom_list=found_nodes,tag_path=new_path)
        return found_nodes
