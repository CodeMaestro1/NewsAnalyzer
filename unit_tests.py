import sys
import os
import unittest
import json
from mock import patch
import unittest
import openpyxl
import os
from Project import read_files, write_files, jaccard_index, BPlusTree


class TestReadFile(unittest.TestCase):

    @classmethod
    def setUp(self):
        print("setUp was called before the unit test")
        self.bpt_instance = BPlusTree()

    def test_read_pairs_from_file(self):
        # Test case 1: Invalid file path
        file_to_read_categories_name_2 = r"\path\to\invalid\file.txt"
        expected_result = {}
        result = read_files.read_pairs_from_file(file_to_read_categories_name_2, self.bpt_instance)
        self.assertEqual(result, expected_result)

        # Test case 2: Empty file
        file_to_read_categories_name_3 = r"C:\Users\user\Downloads\NewsAnalyzer-main\empty.txt"
        expected_result = {}
        result = read_files.read_pairs_from_file(file_to_read_categories_name_3, self.bpt_instance)
        self.assertEqual(result, expected_result)

        # Test case 3: Valid file path
        file_to_read_categories_name = r"C:\Users\mypc1\Desktop\Shared_Project\NewsAnalyzer\category_docId.txt"
        expected_result = {
            "Category_A": {'1', '2', '3', '4'},
            "Category_B": {'5', '6', '7'},
            "Category_C": {'8', '9'}
        }
        result = read_files.read_pairs_from_file(file_to_read_categories_name, self.bpt_instance)
        self.assertEqual(result, expected_result)

class TestJaccardIndex(unittest.TestCase):

    
    def setUp(self):
        print("setUp was called at the beginning of the unit test")
        file_to_read_categories = r"C:\Users\mypc1\Desktop\Shared_Project\NewsAnalyzer\category_docId.txt"
        file_to_read_term = r"C:\Users\mypc1\Desktop\Shared_Project\NewsAnalyzer\docID_term.txt"
        file_to_read_stems = r"stem_term.txt"
        bpt_categories = BPlusTree(10)
        bpt__term = BPlusTree(10)
        bpt_stems = BPlusTree(10)
        returned_data_categories = read_files.read_pairs_from_file(file_to_read_categories, bpt_categories)
        returned_data_term = read_files.read_pairs_from_file(file_to_read_term, bpt__term)
        returned_data_stems = read_files.read_pairs_from_file(file_to_read_stems, bpt_stems)
        self.jaccard_instance = jaccard_index(returned_data_categories, returned_data_term, returned_data_stems)


    def tearDown(self):
        print("tearDown was called after the unit test")

    def test_calculate_jaccard_index(self):
        # Test case 1: Valid file path
        result_dict = self.jaccard_instance.calculate_jaccard_index()
        # with open(r'C:\Users\user\Downloads\NewsAnalyzer-main\sleeplessness.json', 'r') as json_file:
        #     expected_result = json.load(json_file)
        # expected_result = {}
        small_dict = {
            'stem1': {'Category_A': 0.75, 'Category_B': 0, 'Category_C': 0},
            'stem30': {'Category_A': 0, 'Category_B': 0, 'Category_C': 0.5}
        }
        expected_reult = all(item in result_dict.items() for item in small_dict.items())
        self.assertTrue(expected_reult)
        # self.stem = {"stem1": ["term1", "term2"], "stem2": ["term3", "term4"]}
        # self.category = {"category1": ["doc1", "doc2"], "category2": ["doc3", "doc4"]}
        # expected_result = {
        #     "stem1": {"category1": 1.0, "category2": 0.0},
        #     "stem2": {"category1": 0.0, "category2": 1.0}
        # }
        # result = self.calculate_jaccard_index()
        # self.assertEqual(result, expected_result)

class TestJaccardIndex(unittest.TestCase):
    def test_calculate_jaccard_index(self):
        # Define your test inputs and expected outputs
        input1 = ['term1', 'term2', 'term3']
        input2 = ['term2', 'term3', 'term4']
        expected_output = 0.5  # This is just an example. Replace with your actual expected output.

        # Call the function with the test inputs
        actual_output = jaccard_index.calculate_jaccard_index(input1, input2)

        # Assert that the actual output matches the expected output
        self.assertEqual(expected_output, actual_output)


class TestWriteFiles(unittest.TestCase):
    def setUp(self):
        self.write_files_instance = write_files()
        self.test_data = {"stem1": {"category_A": 0.5, "category_B": 0.3}, "stem2": {"category_C": 0.4}}
        self.write_files_instance.data_to_write = self.test_data
        self.test_file = "test_file"

    def test_write_json(self):
        # Call the method with the test file name
        self.write_files_instance.write_json(self.test_file)

        # Check that the file was created
        self.assertTrue(os.path.exists(f"{self.test_file}.json"))

        # Check that the data in the file matches the test data
        with open(f"{self.test_file}.json", 'r') as file:
            data = json.load(file)
            self.assertEqual(data, self.test_data)

    def tearDown(self):
        # Remove the test file
        os.remove(f"{self.test_file}.json")


class TestWriteFiles(unittest.TestCase):
    def setUp(self):
        self.write_files_instance = write_files()
        self.test_data = {"stem1": {"category1": 0.5, "category2": 0.3}, "stem2": {"category1": 0.4}}
        self.write_files_instance.data_to_write = self.test_data
        self.test_file = "test_file"

    def test_write_xlsx(self):
        # Call the method with the test file name
        self.write_files_instance.write_xlsx(self.test_file)

        # Check that the file was created
        self.assertTrue(os.path.exists(f"{self.test_file}.xlsx"))

        # Check that the data in the file matches the test data
        wb = openpyxl.load_workbook(f"{self.test_file}.xlsx")
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            stem, category, jaccard_index = row
            self.assertIn(stem, self.test_data)
            self.assertIn(category, self.test_data[stem])
            self.assertEqual(jaccard_index, self.test_data[stem][category])

    def tearDown(self):
        # Remove the test file
        os.remove(f"{self.test_file}.xlsx")


class TestProjectMethods(unittest.TestCase):
    def setUp(self):
        self.project_instance = Project()
        self.project_instance.jaccard_index = {
            "stem1": {"category1": 0.5, "category2": 0.3},
            "stem2": {"category1": 0.4, "category3": 0.6}
        }

    def test_get_most_relevant_stems_for_category(self):
        category = "category1"
        k = 1
        expected_output = ["stem1"]
        actual_output = self.project_instance.get_most_relevant_stems_for_category(category, k)
        self.assertEqual(expected_output, actual_output)

    def test_get_most_relevant_categories_for_stem(self):
        stem = "stem2"
        k = 1
        expected_output = ["category3"]
        actual_output = self.project_instance.get_most_relevant_categories_for_stem(stem, k)
        self.assertEqual(expected_output, actual_output)

if __name__ == '__main__':
    sys.exit(unittest.main())
