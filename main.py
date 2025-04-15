import sys
import os
import numpy as np
import pandas as pd
import cv2
from alive_progress import alive_bar
import time
import db_pazienti as db
from subject import Subject
import utils

WORKDIR = "C:\\Users\\Emanuele\\Desktop\\Dati_CRC\\"
PARENT_FOLDER = WORKDIR + "Anno_3\\"
SUBJECT_FOLDER = PARENT_FOLDER + "Soggetti\\"
TASKS_FOLDER = PARENT_FOLDER + "Tasks\\"
# ANAGRAFICA_FILE = WORKDIR + "anagrafica_crc.csv"
# CODICI_FILE = WORKDIR + "codici_crc.csv"

ANAGRAFICA_FILE = WORKDIR + "anagrafica.csv"
CODICI_FILE = WORKDIR + "codici.csv"
MISSING_TASKS_FILE = WORKDIR + "missing_tasks_crc.txt"
ANNO = "Anno_3"


def main():
    """ Main function """
    if not os.path.exists(ANAGRAFICA_FILE) or not os.path.exists(CODICI_FILE):
        db.subjects_code_creation(SUBJECT_FOLDER, ANAGRAFICA_FILE, CODICI_FILE)

        print("Anagrafica and codici files created!")

        return 0
    else:
        # Read the anagrafica_crc.csv file
        anagrafica_df = pd.read_csv(ANAGRAFICA_FILE, sep=";")

        # Read the codici_crc.csv file
        codici_df = pd.read_csv(CODICI_FILE, sep=",")
        codici_df = codici_df.convert_dtypes()

        # Remove whitespaces from column Anno
        codici_df[ANNO] = codici_df[ANNO].str.replace(" ", "")

        # Print the dataframes
        # print(anagrafica_df.to_string())
        # print(codici_df.to_string())

        # os.walk is an iterator, next is used to get the next element of the iterator,
        # [1] is used to get the directory names from the tuple returned by os.walk
        # (dirpath, dirnames, filenames)
        subject_directories = next(os.walk(SUBJECT_FOLDER))[1]

        # Remove the CRC folder from the list of subject directories
        subject_directories = [x for x in subject_directories if not x.startswith("CRC")]

        # Number of subjects in the folder
        print(f"Number of subjects in the folder: {len(subject_directories)}")

        # List of Task that must be present in the subject folder
        task_list = ["Task_" + str(i) for i in range(1, 23)]

        # print(subject_directories[0])
        #
        # current_subject = Subject(native_code=subject_directories[0],
        #                           folder_path=SUBJECT_FOLDER + subject_directories[0],
        #                           new_code="")
        #
        # print(current_subject.get_new_code(codici_df, ANNO))
        #
        # # print(f"Elements in folder: {current_subject.get_number_of_elements_in_folder()}")
        # # print(f"Images in folder: {current_subject.get_number_of_files_in_images_folder()}")
        # # print(f"Csv file in folder: {current_subject.get_number_of_csv_files_in_folder()}")
        #
        # if current_subject.get_number_of_csv_files_in_folder() < 21:
        #     if current_subject.check_if_anagrafica_txt_is_present:
        #         missing_csv_list = current_subject.get_list_of_missing_csv_files()
        #         print(f"Missing csv: {missing_csv_list}")
        # else:
        #     print("All csv tasks present")
        #
        # if current_subject.get_number_of_files_in_images_folder() < 25:
        #     missing_images_list = current_subject.get_list_of_missing_images_files()
        #
        #     print(f"Missing images: {missing_images_list}")
        # else:
        #     print("All images present")

        # get the Id list from codici_df dataframe
        id_list = codici_df["Id"].tolist()

        # get the Anno list from codici_df dataframe
        anno_list = codici_df[ANNO].tolist()

        # Replace the NaN values with empty string
        anno_list = ["" if pd.isna(x) else x for x in anno_list]

        # print(f"Id list {len(id_list)}: {id_list}")
        # print(f"Anno list {len(anno_list)}: {anno_list}")

        task_folder_list_new = ["Task_" + str(i) for i in range(1, 22)]

        # Create empty folder for each task in task_folder_list_new
        for task in task_folder_list_new:
            if not os.path.exists(TASKS_FOLDER + task):
                os.makedirs(TASKS_FOLDER + task)

        count = 0

        # Iterate over both lists at the same time using zip
        for id, anno in zip(id_list, anno_list):
            # List the Subjects that have no partecipated to the test in that year
            if anno == "":
                count += 1

                # Create empty folder for the subject in Sogggetti folder
                if not os.path.exists(SUBJECT_FOLDER + id):
                    os.makedirs(SUBJECT_FOLDER + id)

                # Create an empty image for each task in task_folder_list_new with the name of the subject
                for task in task_folder_list_new:
                    img_white = np.zeros([1080, 1920, 3], dtype=np.uint8)
                    img_white.fill(255)
                    cv2.imwrite(TASKS_FOLDER + task + "\\" + id + "_" + task + ".png", img_white)

        print(f"Total missing Subject for {ANNO}: {count}")

        with alive_bar(len(subject_directories), title='Processed Subjects') as bar:
            for count, subject_folder_code in enumerate(subject_directories):
                bar()
                try:
                    # print(count, subject_folder_code)

                    # Get the path of the subject folder
                    subject_path = SUBJECT_FOLDER + subject_folder_code

                    # Get the path of the subject images folder
                    subject_images_path = subject_path + "\\Images\\"

                    # Get the row of the subject in the codici_df dataframe
                    subject_row = codici_df.loc[codici_df[ANNO] == subject_folder_code]

                    # Get the personal code of the subject
                    subject_personal_code = subject_row['Id'].values[0]

                    # Get the list of images in the subject images folder
                    subject_images_list = utils.get_images_in_folder(subject_images_path)

                    # Get the base name of the images in the subject images folder
                    subject_images_list_base = [os.path.splitext(os.path.basename(i))[0] for i in subject_images_list]

                    # Get the list of missing tasks for the current subject
                    missing_task = [x for x in task_list if x not in subject_images_list_base]

                    # Get the list of the path of the missing tasks
                    missing_tasks_path_list = [subject_images_path + str(x) + ".png" for x in missing_task]

                    # Concatenate the list of missing tasks with the list of images
                    complete_images_list = missing_tasks_path_list + subject_images_list

                    # Sort the list of images by the task number
                    complete_images_list = sorted(complete_images_list,
                                                  key=lambda x: int(os.path.splitext(os.path.basename(x))[0].
                                                                    split("_")[1]))

                    # Variable for new task numeration
                    task_updated_value = 1

                    # Iterate over the list of images
                    for task_num, image_task in enumerate(complete_images_list):
                        # print(task_num, image_task)

                        # Get the base filename of the image
                        base_filename = os.path.splitext(os.path.basename(image_task))[0]

                        # Logic for the new task numeration
                        if base_filename == "Task_2" or base_filename == "Task_3" or \
                           base_filename == "Task_6" or base_filename == "Task_26":
                            continue
                        elif base_filename == "Task_4" or base_filename == "Task_5":
                            if base_filename.split("_")[1] == "5":
                                task_updated_value += 1
                        else:
                            task_updated_value += 1

                        # Build the new task folder name
                        task_folder_name = "Task_" + str(task_updated_value)

                        # Build the new filename for the image
                        new_task_name = subject_personal_code + "_Task_" + str(task_updated_value) + ".png"

                        # Build the new task filename path
                        current_task_folder = TASKS_FOLDER + task_folder_name + "\\"

                        # Complete path to save the image in his new folder
                        new_task_filename_path = TASKS_FOLDER + task_folder_name + "\\" + new_task_name

                        # Create directory of the Task if not exists
                        if current_task_folder is not None and not os.path.exists(current_task_folder):
                            os.makedirs(current_task_folder)

                        # If the task is not missing, crop and resize the image
                        if base_filename not in missing_task:
                            # print(f"Salvo: {new_task_filename_path}")
                            # Crop and resize the image, then save it
                            utils.crop_and_resize_image(image_task, new_task_filename_path)
                            utils.crop_and_resize_image(image_task, image_task)
                        else:
                            print(f"Non c'è il task {base_filename}")
                            img = np.zeros([1080, 1920, 3], dtype=np.uint8)
                            img.fill(255)
                            # print(f"Salvo: {new_task_filename_path}")
                            cv2.imwrite(new_task_filename_path, img)

                    # Save the list of missing tasks in the Missing_tasks_crc.txt file
                    if missing_task:
                        # Save the list in Missing_tasks_crc.txt
                        with open(MISSING_TASKS_FILE, "a") as f:
                            f.write(subject_folder_code + ":" + "\n")
                            f.write(str(missing_task) + "\n")

                    # Rename the subject folder
                    os.rename(subject_path, SUBJECT_FOLDER + subject_personal_code)

                except Exception as e:
                    print("Error: ", e)
                    continue

    return 0


if __name__ == '__main__':
    main()
