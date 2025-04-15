from dataclasses import dataclass
import pandas as pd
import glob
import os
import re

# Define task renumbering map: original task number → new task number
# Tasks 1, 2, and 5 are skipped
TASK_RENUMBERING_MAP = {
    1: None, 2: None, 5: None,  # Skip these tasks
    3: 1,  # Task3 becomes Task1
    4: 2,  # Task4 becomes Task2
    6: 3,  # Task6 becomes Task3
    7: 4, 8: 5, 9: 6, 10: 7,
    11: 8, 12: 9, 13: 10, 14: 11,
    15: 12, 16: 13, 17: 14, 18: 15,
    19: 16, 20: 17, 21: 18, 22: 19,
    # Task26 (special case) is handled separately in the main.py
    26: None
}

# Reverse mapping for reference (new task number → original task number)
TASK_ORIGINAL_MAP = {new_num: old_num for old_num, new_num in TASK_RENUMBERING_MAP.items() if new_num is not None}


def get_list_of_tasks(extension: str = "csv"):
    """
    Get the list of tasks in the subject folder

    Args:
        extension (str): Type of files to get tasks for ("csv" or "images")

    Returns:
        list: Task list in TaskN format
    """
    if extension == "csv":
        # For CSV, we need tasks 1-21 (original numbering)
        # After renumbering and filtering, it's 1-19 (new numbering)
        return [f"Task{i}" for i in range(1, 20)]
    elif extension == "images":
        # For images, we need all tasks except 1, 2, 5, 26 (original numbering)
        # After renumbering, it's 1-19 (new numbering)
        return [f"Task{i}" for i in range(1, 20)]


def normalize_task_name(filename):
    """
    Normalize various task naming patterns to a standard 'TaskN' format (without underscore)

    Args:
        filename (str): The filename to normalize

    Returns:
        str: The normalized task name in 'TaskN' format, or None if not a task
        int: The original task number (before renumbering), or None if not a task
    """
    # Extract task number from various patterns
    task_number = None

    # In 'Task_N' format, convert to 'TaskN'
    if re.match(r"Task_\d+", filename):
        task_number = int(re.search(r"Task_(\d+)", filename).group(1))

    # In 'TaskN_' format
    elif re.match(r"Task\d+_", filename):
        task_number = int(re.search(r"Task(\d+)_", filename).group(1))

    # In 'TaskN' format (without trailing underscore)
    elif re.match(r"Task\d+$", filename) or re.match(r"Task\d+[^_]", filename):
        task_number = int(re.search(r"Task(\d+)", filename).group(1))

    # Try to extract any task number from other formats
    else:
        match = re.search(r"Task[_]?(\d+)", filename)
        if match:
            task_number = int(match.group(1))

    # If we found a task number, normalize it
    if task_number is not None:
        return f"Task{task_number}", task_number

    # Not a task
    return None, None


def get_renumbered_task_name(original_task_number):
    """
    Convert original task number to the renumbered task number

    Args:
        original_task_number (int): Original task number

    Returns:
        str: Renumbered task name in TaskN format, or None if task should be skipped
    """
    if original_task_number in TASK_RENUMBERING_MAP:
        new_number = TASK_RENUMBERING_MAP[original_task_number]
        if new_number is not None:
            return f"Task{new_number}"
    return None


@dataclass
class Subject:
    native_code: str
    folder_path: str
    new_code: str

    def get_new_code(self, codici_df: pd.DataFrame, year: str):
        """ Get the new code for the subject from the codici_df dataframe"""
        self.new_code = codici_df.loc[codici_df[year] == self.native_code].Id.values[0]
        return self.new_code

    def get_number_of_elements_in_folder(self):
        """ Count the number of elements in the subject folder"""
        return len(os.listdir(self.folder_path))

    def get_number_of_files_in_images_folder(self):
        """ Get the number of files in the subject images folder"""
        if os.path.exists(self.folder_path + "\\Images\\"):
            return len(os.listdir(self.folder_path + "\\Images\\"))
        else:
            return 0

    def get_number_of_csv_files_in_folder(self):
        """ Get the number of csv files in the subject folder"""
        return len([name for name in os.listdir(self.folder_path) if name.endswith(".csv")])

    def check_if_anagrafica_txt_is_present(self):
        """ Check if the anagrafica.txt file is present in the subject folder"""
        return True if glob.glob(self.folder_path + "/*Anagrafica*.txt") else False

    def get_list_of_csv_files(self, use_renumbering=True):
        """
        Get the list of csv files in the subject folder

        Args:
            use_renumbering (bool): Whether to use task renumbering

        Returns:
            list: List of task names in TaskN format
        """
        csv_files = glob.glob(self.folder_path + "/*.csv")

        task_list = []
        for csv_file in csv_files:
            # Get just the filename without path and extension
            filename = os.path.splitext(os.path.basename(csv_file))[0]

            # Normalize to TaskN format and get original task number
            normalized_name, original_task_number = normalize_task_name(filename)

            if normalized_name:
                # If renumbering is enabled, convert to new task number
                if use_renumbering and original_task_number:
                    renumbered_name = get_renumbered_task_name(original_task_number)
                    if renumbered_name:
                        task_list.append(renumbered_name)
                else:
                    task_list.append(normalized_name)

        # Remove duplicates
        task_list = list(set(task_list))

        # Sort by task number
        task_list = sorted(task_list, key=lambda x: int(re.search(r"Task(\d+)", x).group(1)))

        return task_list

    def get_list_of_images_files(self, use_renumbering=True):
        """
        Get the list of images files in the subject folder

        Args:
            use_renumbering (bool): Whether to use task renumbering

        Returns:
            list: List of task names in TaskN format
        """
        image_files = glob.glob(self.folder_path + "\\Images\\*.png")

        task_list = []
        for image_file in image_files:
            # Get just the filename without path and extension
            filename = os.path.splitext(os.path.basename(image_file))[0]

            # Normalize to TaskN format and get original task number
            normalized_name, original_task_number = normalize_task_name(filename)

            if normalized_name:
                # If renumbering is enabled, convert to new task number
                if use_renumbering and original_task_number:
                    renumbered_name = get_renumbered_task_name(original_task_number)
                    if renumbered_name:
                        task_list.append(renumbered_name)
                else:
                    task_list.append(normalized_name)

        # Remove duplicates
        task_list = list(set(task_list))

        # Sort by task number
        task_list = sorted(task_list, key=lambda x: int(re.search(r"Task(\d+)", x).group(1)))

        return task_list

    def get_list_of_missing_csv_files(self):
        """ Get the list of missing csv files in the subject folder"""
        return [x for x in get_list_of_tasks("csv") if x not in self.get_list_of_csv_files()]

    def get_list_of_missing_images_files(self):
        """ Get the list of missing images files in the subject folder"""
        return [x for x in get_list_of_tasks("images") if x not in self.get_list_of_images_files()]