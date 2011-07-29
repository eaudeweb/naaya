# -*- coding: utf-8 -*-
#
from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from Products.NaayaCore.PortletsTool.PortletsTool import PortletsTool
from Products.NaayaCore.PortletsTool.RefTree import manage_addRefTree
from Products.NaayaCore.PortletsTool.RefTreeNode import manage_addRefTreeNode

class RefTreeFunctionalTestCase(NaayaFunctionalTestCase):
    """ Functional testing of RefTree and RefTree Node """
    def afterSetUp(self):
        """
        Tree:
            1
                2
                    4
                    5
                        8
                            10
                        9
                    6
                3
                    7
        """
        self.portlets_tool = self.portal.getPortletsTool()
        manage_addRefTree(self.portlets_tool, 'tree', 'Tree', 'Tree decription', 'en')
        
        self.tree = self.portlets_tool.tree
        
        manage_addRefTreeNode(self.tree, 'node1', 'Node 1', lang="en")
        manage_addRefTreeNode(self.tree, 'node2', 'Node 2', 'node1', lang='en')
        manage_addRefTreeNode(self.tree, 'node3', 'Node 3', 'node1', lang='en')
        manage_addRefTreeNode(self.tree, 'node4', 'Node 4', 'node2', lang='en')
        manage_addRefTreeNode(self.tree, 'node5', 'Node 5', 'node2', lang='en')
        manage_addRefTreeNode(self.tree, 'node6', 'Node 6', 'node2', lang='en')
        manage_addRefTreeNode(self.tree, 'node7', 'Node 7', 'node3', lang='en')
        manage_addRefTreeNode(self.tree, 'node8', 'Node 8', 'node5', lang='en')
        manage_addRefTreeNode(self.tree, 'node9', 'Node 9', 'node5', lang='en')
        manage_addRefTreeNode(self.tree, 'node10', 'Node 10', 'node8', lang='en')
        transaction.commit()
    def test_moveRefTreeNode(self):
        """
            1. Move 8 after 4
            2. Move 3 before 4
            2. Move 3 on root path
            3. Move 2 as child of 9 - raise ValueError
        """
        self.tree.move(self.tree.node8, 'node2', after='node4')
        self.assertEqual(self.tree.node8.parent, 'node2')
        self.assertEqual(self.tree.node4.weight, 0)
        self.assertEqual(self.tree.node8.weight, 1)
        self.assertEqual(self.tree.node5.weight, 2)
        self.assertEqual(self.tree.node6.weight, 3)
        
        self.tree.move(self.tree.node3, 'node2', before='node4')
        self.assertEqual(self.tree.node3.parent, 'node2')
        self.assertEqual(self.tree.node3.weight, 0)
        self.assertEqual(self.tree.node4.weight, 1)
        self.assertEqual(self.tree.node8.weight, 2)
        self.assertEqual(self.tree.node5.weight, 3)
        self.assertEqual(self.tree.node6.weight, 4)
        
        self.tree.move(self.tree.node3, None)
        self.assertEqual(self.tree.node3.parent, None)
        self.assertEqual(self.tree.node3.weight, 1)
        
        self.tree.move(self.tree.node3, None, before='node1')
        self.assertEqual(self.tree.node3.weight, 0)
        self.assertEqual(self.tree.node1.weight, 1)
        
        self.assertRaises(ValueError, self.tree.move, self.tree.node2, 'node9')
