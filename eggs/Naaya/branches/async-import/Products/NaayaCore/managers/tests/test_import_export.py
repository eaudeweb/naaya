# -*- coding=utf-8 -*-
import unittest
import os.path

from Products.NaayaCore.managers.import_export import CSVReader


class CSVReaderTest(unittest.TestCase):

    def read_csv(self, filename):
        file = open(os.path.join(os.path.dirname(__file__), "data", filename),
                    'r')
        reader = CSVReader(file, "comma", "utf-8")
        result = reader.read()
        file.close()
        return result

    def test_successful_read(self):
        data, exc = self.read_csv("csv_valid.csv")
        self.assertEqual(exc, '')
        tiers = []
        animals = []
        for mapping in data:
            self.assertEqual(set(mapping.keys()), set(['Tier', 'Animal']))
            tiers.append(mapping['Tier'].decode('utf-8'))
            animals.append(mapping['Animal'].decode('utf-8'))
        self.assertEqual(len(tiers), 3)
        self.assertEqual(len(animals), 3)
        self.assertEqual(set(animals), set([u'Male Dog', u'Kitten',
                                            'Black Swan']))
        self.assertEqual(set(tiers), set([u'Rüde', u'Kätzchen',
                                          u'Schwarzer Schwan']))

    def test_invalid_read(self):
        data, exc = self.read_csv("csv_invalid.csv")
        self.assertEqual(data, None)
        self.assertTrue(isinstance(exc, UnicodeDecodeError))

    def test_empty(self):
        data, exc = self.read_csv("csv_empty.csv")
        self.assertEqual(data, None)
        self.assertTrue(isinstance(exc, StopIteration))

    def test_only_header(self):
        data, exc = self.read_csv("csv_only_header.csv")
        self.assertEqual(data, [])
        self.assertEqual(exc, '')
