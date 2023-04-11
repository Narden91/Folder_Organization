import sys
import os
import numpy as np
import pandas as pd
import cv2
import db_pazienti as db
import utils

WORKDIR = "C:\\Users\\Emanuele\\Desktop\\Dati_CRC\\"
PARENT_FOLDER = WORKDIR + "Anno_1\\"
SUBJECT_FOLDER = PARENT_FOLDER + "Soggetti\\"
TASKS_FOLDER = PARENT_FOLDER + "Tasks\\"
ANAGRAFICA_FILE = WORKDIR + "anagrafica_crc.csv"
CODICI_FILE = WORKDIR + "codici_crc.csv"
ANNO = "Anno_1"


def main():
    if not os.path.exists(ANAGRAFICA_FILE) or not os.path.exists(CODICI_FILE):
        db.subjects_code_creation(SUBJECT_FOLDER, ANAGRAFICA_FILE, CODICI_FILE)

        print("Anagrafica and codici files created!")

        return 0
    else:
        # Read the anagrafica_crc.csv file
        anagrafica_df = pd.read_csv(ANAGRAFICA_FILE, sep=",")

        # Read the codici_crc.csv file
        codici_df = pd.read_csv(CODICI_FILE, sep=",")
        codici_df = codici_df.convert_dtypes()

        # Print the dataframes
        # print(anagrafica_df.to_string())
        # print(codici_df.to_string())

        # os.walk is an iterator, next is used to get the next element of the iterator,
        # [1] is used to get the directory names from the tuple returned by os.walk
        # (dirpath, dirnames, filenames)
        subject_directories = next(os.walk(SUBJECT_FOLDER))[1]

        # Remove the CRC folder from the list of subject directories
        subject_directories = [x for x in subject_directories if not x.startswith("CRC")]

        # print(subject_directories)

        for count, subject_folder_code in enumerate(subject_directories):

            try:
                # print(count, subject)

                # Get the path of the subject folder
                subject_path = SUBJECT_FOLDER + subject_folder_code

                # Get the path of the subject images folder
                subject_images_path = subject_path + "\\Images\\"

                # Get the row of the subject in the anagrafica_df dataframe
                subject_row = codici_df.loc[codici_df[ANNO] == subject_folder_code]

                # Get the personal code of the subject
                subject_personal_code = subject_row['Id'].values[0]

                # Get the list of images in the subject images folder
                subject_images_list = utils.get_images_in_folder(subject_images_path)

                # Print the list of images
                # print(subject_images_list)

                task_updated_value = 1

                # Iterate over the list of images
                for task_num, image_task in enumerate(subject_images_list):
                    # print(task_num, image)

                    # Get the base filename of the image
                    base_filename = os.path.splitext(os.path.basename(image_task))[0]

                    if base_filename == "Task_2" or base_filename == "Task_3" or \
                       base_filename == "Task_6" or base_filename == "Task_26":
                        continue
                    elif base_filename == "Task_4" or base_filename == "Task_5":
                        if base_filename.split("_")[1] == "5":
                            task_updated_value += 1
                    else:
                        task_updated_value += 1

                    task_folder_name = "Task_" + str(task_updated_value)

                    new_task_name = subject_personal_code + "_Task_" + str(task_updated_value) + ".png"

                    current_task_folder = TASKS_FOLDER + task_folder_name + "\\"

                    new_task_filename_path = TASKS_FOLDER + task_folder_name + "\\" + new_task_name

                    # Create directory if not exists
                    if current_task_folder is not None and not os.path.exists(current_task_folder):
                        os.makedirs(current_task_folder)

                    # Crop and resize the image, then save it
                    utils.crop_and_resize_image(image_task, new_task_filename_path)
                    utils.crop_and_resize_image(image_task, image_task)

                # Rename the subject folder
                os.rename(subject_path, SUBJECT_FOLDER + subject_personal_code)
            except Exception as e:
                print("Error: ", e)
                continue

    return 0


if __name__ == '__main__':
    main()
