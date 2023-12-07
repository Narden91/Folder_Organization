import os
import pytest


@pytest.fixture
def root_directory():
    return 'C:\\Users\\Emanuele\\Desktop\\Dati_CRC2\\Anno_2\\Tasks\\'  # Replace with the actual path


@pytest.fixture
def expected_file_count():
    return 144


def count_files_in_directory(directory):
    """ Counts the number of files in the given directory. """
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])


def test_file_count_in_subfolders(root_directory, expected_file_count):
    """ Test to check if each subfolder in the root directory has the expected number of files. """
    for subdir, _, _ in os.walk(root_directory):
        if subdir != root_directory:  # to skip the root directory itself
            file_count = count_files_in_directory(subdir)
            try:
                assert file_count == expected_file_count, f"Subfolder {subdir} contains {file_count} files, expected {expected_file_count}"
            except AssertionError as e:
                print(e)
                raise

