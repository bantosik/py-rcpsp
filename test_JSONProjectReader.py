from unittest import TestCase
from JsonProjectReader import JSONProjectReader
import os

__author__ = 'bartek'

FILENAME = 'testFiles/sampleProject.json'

class TestJSONProjectReader(TestCase):
    def test_read(self):
        jsonReader = JSONProjectReader()
        jsonReader.read(os.path.realpath(FILENAME))
