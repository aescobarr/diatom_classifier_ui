from django.test import TestCase
from classifier.classifier import create_temp_dir, unzip_to_dir, classify
import os
from pathlib import Path

# Create your tests here.
class TestFileCreation(TestCase):
    def test_temp_dir_creation(self):
        temp_dir = create_temp_dir()
        path_temp_dir = Path(temp_dir.name)
        self.assertTrue( path_temp_dir.is_dir(), f"temp dir {path_temp_dir} should exist, does not" )
        temp_dir.cleanup()
        self.assertFalse(path_temp_dir.is_dir(), f"temp dir {path_temp_dir} should NOT exist after cleanup, it does")

    def test_temp_dir_and_uncompress(self):
        temp_dir = create_temp_dir()
        path_temp_dir = Path(temp_dir.name)
        dest_dir = os.path.join(path_temp_dir, "exploded")
        test_file_path = Path(__file__).parent / "fixtures" / "diatoms.zip"
        unzip_to_dir( str(test_file_path), dest_dir )
        path_dest_dir = Path(dest_dir)
        self.assertTrue( path_dest_dir.is_dir(), f"Destination dir {dest_dir} should exist, does not" )
        dir = os.listdir(path_dest_dir)
        self.assertTrue( len(dir) > 0, f"Destination dir {dest_dir} is empty, it should not be" )
        temp_dir.cleanup()
        self.assertFalse(path_temp_dir.is_dir(), f"temp dir {path_temp_dir} should NOT exist after cleanup, it does")

    # def test_classify(self):
    #     temp_dir = create_temp_dir()
    #     path_temp_dir = Path(temp_dir.name)
    #     dest_dir = os.path.join(path_temp_dir, "exploded")
    #     test_file_path = Path(__file__).parent / "fixtures" / "diatoms.zip"
    #     unzip_to_dir(str(test_file_path), dest_dir)
    #     classify("/home/webuser/dev/python/bento_diatom/doa_diatom_model.pth",pictures_dir=dest_dir, classes=['alive','dead'])