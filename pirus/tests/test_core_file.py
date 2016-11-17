#!python
# coding: utf-8


import os
import sys
import shutil
import unittest

from mongoengine import *

from tests.config import *
from core import pirus



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# API SIGNATURE & TEST PARAMETER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
TU_PIRUS_FILE_PUBLIC_FIELDS = ["id", "name", "type", "size", "status", "upload_offset", "comments", "runs", "create_date", "tags", "md5sum", "url", "upload_url", "source"]




class TestCoreFile(unittest.TestCase):
    """ Test case for pirus core file's features. """



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # PREPARATION
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @classmethod
    def setUpClass(self):
        # Before test we check that we are using the good config file
        if VERSION != "tu": raise Exception("Wrong config file used")
        # Clean test's database 
        self.db = connect(DATABASE_NAME)
        self.db.drop_database(DATABASE_NAME)
        # Clean test's directory
        if os.path.exists(FILES_DIR):
            shutil.rmtree(FILES_DIR)
            os.makedirs(FILES_DIR)
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            os.makedirs(TEMP_DIR)



    @classmethod
    def tearDownClass(self):
        # self.db.drop_database(DATABASE_NAME)
        # shutil.rmtree(TEMP_DIR)
        # shutil.rmtree(FILES_DIR)
        pass



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # TESTS
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_public_fields(self):
        """ Test new file registration """
        self.assertEqual(pirus.files.public_fields(), TU_PIRUS_FILE_PUBLIC_FIELDS)

    def test_total(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

    def test_get_generic(self):
        """ Test new file registration """
        # fields=None, query=None, order=None, offset=None, limit=None, sublvl=0):
        # """
        #     Generic method to get files metadata according to provided filtering options
        # """
        # if fields is None:
        #     fields = PirusFile.public_fields
        # if query is None:
        #     query = {}
        # if order is None:
        #     order = ['-create_date', "name"]
        # if offset is None:
        #     offset = 0
        # if limit is None:
        #     limit = offset + RANGE_MAX
        self.assertEqual(1, 1)

    def test_get_from_id(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

    def test_from_ids(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

    def test_register(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

    def test_edit(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

    def test_delete(self):
        """ Test new file registration """
        self.assertEqual(1, 1)

