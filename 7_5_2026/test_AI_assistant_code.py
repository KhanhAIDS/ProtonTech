import unittest
import tempfile
import os
from io import StringIO
from unittest.mock import patch
from AI_assistant_code import FeatureFilter, ImageFeatures

class TestFeatureFilter(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.valid_csv_path = os.path.join(self.temp_dir.name, 'valid.csv')
        with open(self.valid_csv_path, 'w', encoding='utf-8') as f:
            f.write("filename,SYM_Symmetry_Index,score\n")
            f.write("img1.jpg,0.5,4.0\n")
            f.write("img2.jpg,0.8,2.0\n")
            f.write("img3.jpg,1.0,3.5\n")

        self.invalid_csv_path = os.path.join(self.temp_dir.name, 'invalid.csv')
        with open(self.invalid_csv_path, 'w', encoding='utf-8') as f:
            f.write("filename,wrong_column\n")
            f.write("img1.jpg,0.5\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_calculate_statistics_empty(self):
        filter_tool = FeatureFilter("dummy.csv", 3.0)
        avg_score, avg_sym = filter_tool.calculate_statistics()
        self.assertEqual(avg_score, 0.0)
        self.assertEqual(avg_sym, 0.0)

    def test_calculate_statistics_populated(self):
        filter_tool = FeatureFilter("dummy.csv", 3.0)
        filter_tool.filtered_data = [
            ImageFeatures("img1.jpg", 0.5, 4.0),
            ImageFeatures("img3.jpg", 1.0, 3.5)
        ]
        avg_score, avg_sym = filter_tool.calculate_statistics()
        self.assertEqual(avg_score, 3.75)
        self.assertEqual(avg_sym, 0.75)

    def test_load_and_filter_valid(self):
        filter_tool = FeatureFilter(self.valid_csv_path, 3.0)
        filter_tool.load_and_filter()
        self.assertEqual(len(filter_tool.filtered_data), 2)
        self.assertEqual(filter_tool.filtered_data[0].filename, "img1.jpg")
        self.assertEqual(filter_tool.filtered_data[1].filename, "img3.jpg")

    def test_load_and_filter_missing_columns(self):
        filter_tool = FeatureFilter(self.invalid_csv_path, 3.0)
        with self.assertRaises(ValueError):
            filter_tool.load_and_filter()

    def test_load_and_filter_file_not_found(self):
        filter_tool = FeatureFilter("nonexistent.csv", 3.0)
        with self.assertRaises(FileNotFoundError):
            filter_tool.load_and_filter()

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results(self, mock_stdout):
        filter_tool = FeatureFilter("dummy.csv", 3.0)
        filter_tool.filtered_data = [
            ImageFeatures("img1.jpg", 0.5, 4.0)
        ]
        filter_tool.print_results()
        output = mock_stdout.getvalue()
        self.assertIn("Da tim thay du lieu dat chuan!", output)
        self.assertIn("Tong so anh dat dieu kien: 1", output)

if __name__ == '__main__':
    unittest.main()