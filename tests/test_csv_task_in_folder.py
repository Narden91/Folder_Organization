import os
import pytest


@pytest.fixture
def root_directory():
    return 'C:\\Users\\Emanuele\\Desktop\\Dati_CRC2\\Anno_2\\Soggetti\\'  # Replace with the actual path


@pytest.fixture
def expected_csv_count():
    return 21


def count_csv_files_in_directory(directory):
    """ Counts the number of CSV files in the given directory. """
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) and name.endswith('.csv')])


def test_csv_file_count_in_subfolders(root_directory, expected_csv_count):
    """ Test to check if each subfolder in the root directory has the expected number of CSV files. """
    for item in os.listdir(root_directory):
        subdir = os.path.join(root_directory, item)
        if os.path.isdir(subdir):
            csv_count = count_csv_files_in_directory(subdir)
            try:
                assert csv_count == expected_csv_count, f"Subfolder {subdir} contains {csv_count} CSV files, expected {expected_csv_count}"
            except AssertionError as e:
                print(e)
                raise
