from dataclasses import dataclass
import pandas as pd
import glob
import os
import re


def get_list_of_tasks(extension: str = "csv"):
    """ Get the list of tasks in the subject folder"""
    if extension == "csv":
        return ["Task_" + str(i) for i in range(1, 22)]
    elif extension == "images":
        return ["Task_" + str(i) for i in range(2, 27)]


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

    def get_list_of_csv_files(self):
        """ Get the list of csv files in the subject folder"""

        csv_list = []

        # Regular expression to extract the task name and the number of the task (Task12 -> Task, 12)
        r = re.compile("([a-zA-Z]+)([0-9]+)")

        # Get the list of csv files in the folder
        temp_list = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(self.folder_path + "/*.csv")]

        # Remove everything after the first _ from the task name
        temp_list = [x.split("_")[0] for x in temp_list]

        # Create new list with the task name and the number of the task
        for task in temp_list:
            filename = r.match(task).groups()[0] + "_" + r.match(task).groups()[1]
            csv_list.append(filename)

        # Sort the list by the number of the task
        csv_list = sorted(csv_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("_")[1]))

        return csv_list

    def get_list_of_images_files(self):
        """ Get the list of images files in the subject folder"""

        images_list = []

        # Regular expression to extract the task name and the number of the task (Task12 -> Task, 12)
        r = re.compile("([a-zA-Z]+)([0-9]+)")

        # Get the list of images files in the folder
        images_list = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(self.folder_path + "\\Images\\*.png")]

        # # Remove everything after the first _ from the task name
        # temp_list = [x.split("_")[0] for x in temp_list]
        #
        # # Create new list with the task name and the number of the task
        # for task in temp_list:
        #     filename = r.match(task).groups()[0] + "_" + r.match(task).groups()[1]
        #     images_list.append(filename)

        # Sort the list by the number of the task
        images_list = sorted(images_list, key=lambda x: int(x.split("_")[1]))

        return images_list

    def get_list_of_missing_csv_files(self):
        """ Get the list of missing csv files in the subject folder"""
        return [x for x in get_list_of_tasks("csv") if x not in self.get_list_of_csv_files()]

    def get_list_of_missing_images_files(self):
        """ Get the list of missing images files in the subject folder"""
        return [x for x in get_list_of_tasks("images") if x not in self.get_list_of_images_files()]
