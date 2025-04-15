import os
import sys
import numpy as np
import pandas as pd
import cv2
import re
import glob
from alive_progress import alive_bar
import time

# Define paths
WORKDIR = "C:\\Users\\Emanuele\\Desktop\\Dati_CRC\\"
PARENT_FOLDER = WORKDIR + "Anno_3\\"
SUBJECT_FOLDER = PARENT_FOLDER + "Soggetti\\"
TASKS_FOLDER = PARENT_FOLDER + "Tasks\\"
ANAGRAFICA_FILE = WORKDIR + "anagrafica.csv"
CODICI_FILE = WORKDIR + "codici.csv"
MISSING_TASKS_FILE = WORKDIR + "missing_tasks_crc.txt"
ANNO = "Anno_3"

# Task renumbering map: defines how original task numbers are converted to new ones
# Tasks 1, 2, and 5 are skipped as per requirements
TASK_RENUMBERING_MAP = {
    1: None, 2: None, 5: None,  # Skip these tasks
    3: 1,  # Task3 becomes Task1
    4: 2,  # Task4 becomes Task2
    6: 3,  # Task6 becomes Task3
    7: 4, 8: 5, 9: 6, 10: 7,
    11: 8, 12: 9, 13: 10, 14: 11,
    15: 12, 16: 13, 17: 14, 18: 15,
    19: 16, 20: 17, 21: 18, 22: 19,
    26: None  # Task26 is skipped
}

# Reverse mapping for reference (new task number → original task number)
TASK_ORIGINAL_MAP = {new_num: old_num for old_num, new_num in TASK_RENUMBERING_MAP.items() if new_num is not None}

# Acquired Image dimensions
WIDTH_ACQUIRED = 1280
HEIGHT_ACQUIRED = 720

# Image dimensions
WIDTH_IMAGE = 1920
HEIGHT_IMAGE = 1080


def normalize_task_name(filename):
    """
    Normalize various task naming patterns to a standard 'TaskN' format (without underscore)

    Args:
        filename (str): The filename to normalize

    Returns:
        str: The normalized task name in 'TaskN' format, or None if not a task
        int: The extracted task number, or None if not a task
    """
    # In 'Task_N' format, convert to 'TaskN'
    if re.match(r"Task_\d+", filename):
        task_number = int(re.search(r"Task_(\d+)", filename).group(1))
        return f"Task{task_number}", task_number

    # In 'TaskN_' format, just remove the trailing underscore
    if re.match(r"Task\d+_", filename):
        task_number = int(re.search(r"Task(\d+)_", filename).group(1))
        return f"Task{task_number}", task_number

    # Already in 'TaskN' format (without trailing underscore)
    if re.match(r"Task\d+$", filename) or re.match(r"Task\d+[^_]", filename):
        task_number = int(re.search(r"Task(\d+)", filename).group(1))
        return f"Task{task_number}", task_number

    # Try to extract any task number if possible from other formats
    match = re.search(r"Task[_]?(\d+)", filename)
    if match:
        task_number = int(match.group(1))
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


def get_images_in_folder(images_folder_path, image_extension=".png"):
    """
    Get the list of images in the folder

    Args:
        images_folder_path (str): The path of the folder
        image_extension (str): The extension of the images

    Returns:
        list: The list of image file paths in the folder
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(images_folder_path):
        os.makedirs(images_folder_path)
        return []

    # Get all the images in the folder
    images_file_list = [f.path for f in os.scandir(images_folder_path) if
                        f.is_file() and f.path.endswith(image_extension)]

    # Sort by filename
    images_file_list = sorted(images_file_list, key=lambda x: len(x))

    return images_file_list


def create_white_image(width=WIDTH_IMAGE, height=HEIGHT_IMAGE):
    """
    Create a blank white image with the specified dimensions

    Args:
        width (int): Image width in pixels
        height (int): Image height in pixels

    Returns:
        numpy.ndarray: A white image
    """
    img = np.zeros([height, width, 3], dtype=np.uint8)
    img.fill(255)
    return img


def crop_and_resize_image(source_path, destination_path):
    """
    Read an image, crop it to the specified coordinates, resize it,
    and save it to the specified destination path

    Args:
        source_path (str): The path to the image to crop and resize
        destination_path (str): The path to save the processed image
    """
    try:
        # Read the image
        img = cv2.imread(source_path)

        # Get image dimensions
        height, width, channels = img.shape

        # Crop the image to specified coordinates
        cropped = img[0:HEIGHT_ACQUIRED, 0:WIDTH_ACQUIRED]

        # Resize the cropped image to specified dimensions
        resized = cv2.resize(cropped, (WIDTH_IMAGE, HEIGHT_IMAGE))

        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Save the resized image
        cv2.imwrite(destination_path, resized)
    except FileNotFoundError:
        print(f"File {source_path} NOT found!")
    except Exception as e:
        print(f"Error processing {source_path}: {e}")


def read_csv_files():
    """
    Read the anagrafica.csv and codici.csv files

    Returns:
        tuple: (anagrafica_df, codici_df) - pandas DataFrames containing the CSV data
    """
    try:
        # Read the anagrafica.csv file - note it uses semicolon delimiter
        anagrafica_df = pd.read_csv(ANAGRAFICA_FILE, sep=";", encoding='utf-8')

        # Read the codici.csv file
        codici_df = pd.read_csv(CODICI_FILE, sep=",", encoding='utf-8')
        codici_df = codici_df.convert_dtypes()

        # Remove whitespaces from column Anno_3
        if ANNO in codici_df.columns:
            codici_df[ANNO] = codici_df[ANNO].str.strip()

        return anagrafica_df, codici_df

    except Exception as e:
        print(f"Error reading CSV files: {e}")
        sys.exit(1)


def main():
    """
    Main function to process subjects and tasks
    """
    # Read CSV files
    anagrafica_df, codici_df = read_csv_files()

    # Get the list of tasks after renumbering (Task1 through Task19)
    new_task_list = [f"Task{i}" for i in range(1, 20)]

    # Create task folders for each renumbered task
    for task in new_task_list:
        task_folder_path = os.path.join(TASKS_FOLDER, task)
        if not os.path.exists(task_folder_path):
            os.makedirs(task_folder_path)

    # Get subject directories - these are the present subjects
    subject_directories = next(os.walk(SUBJECT_FOLDER))[1]
    subject_directories = [x for x in subject_directories if not x.startswith("CRC")]
    print(f"Number of existing subjects in the folder: {len(subject_directories)}")

    # Get lists of subjects from codici_df
    id_list = codici_df["Id"].tolist()
    anno_list = []

    # Handle the case where Anno_3 column might not exist
    if ANNO in codici_df.columns:
        anno_list = codici_df[ANNO].tolist()
        # Replace NaN values with empty string
        anno_list = ["" if pd.isna(x) else x for x in anno_list]
    else:
        # If Anno_3 doesn't exist, all subjects are considered missing
        anno_list = ["" for _ in id_list]

    # Process missing subjects - create folders and white images
    missing_count = 0

    print("Processing missing subjects...")
    for id_code, anno_code in zip(id_list, anno_list):
        # Skip if the subject has a code for the current year
        if anno_code != "":
            continue

        missing_count += 1

        # Create empty folder for the subject if it doesn't exist
        subject_folder = os.path.join(SUBJECT_FOLDER, id_code)
        if not os.path.exists(subject_folder):
            os.makedirs(subject_folder)
            print(f"Created missing subject folder: {id_code}")

        # Create white images for each task
        for task in new_task_list:
            img_white = create_white_image()
            task_file_path = os.path.join(TASKS_FOLDER, task, f"{id_code}_{task}.png")
            cv2.imwrite(task_file_path, img_white)

    print(f"Total missing subjects for {ANNO}: {missing_count}")

    # Clear missing tasks file before writing new content
    if os.path.exists(MISSING_TASKS_FILE):
        open(MISSING_TASKS_FILE, 'w').close()

    # Process existing subjects
    print("\nProcessing existing subjects...")
    with alive_bar(len(subject_directories), title='Processed Subjects') as bar:
        for subject_folder_code in subject_directories:
            try:
                # Get paths
                subject_path = os.path.join(SUBJECT_FOLDER, subject_folder_code)
                subject_images_path = os.path.join(subject_path, "Images")

                # Get subject's ID from codici_df
                subject_row = codici_df.loc[codici_df[ANNO] == subject_folder_code]

                # Skip if subject not found in codici_df
                if subject_row.empty:
                    print(f"Warning: Subject {subject_folder_code} not found in codici.csv")
                    bar()
                    continue

                subject_id = subject_row['Id'].values[0]

                # List of original tasks (unnumbered)
                original_task_list = [f"Task{i}" for i in range(1, 23)] + ["Task26"]

                # Get images in the subject's Images folder
                subject_images_list = get_images_in_folder(subject_images_path)

                # Create mapping from original task name to file path
                original_task_to_path = {}
                for image_path in subject_images_list:
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    normalized, original_number = normalize_task_name(base_name)
                    if normalized:
                        original_task_to_path[normalized] = image_path

                # Find missing tasks
                missing_tasks = [task for task in original_task_list if task not in original_task_to_path]

                # Process each task with the new numbering scheme
                for original_number in range(1, 27):  # Include special case Task26
                    # Skip tasks that should be excluded
                    if original_number not in TASK_RENUMBERING_MAP or TASK_RENUMBERING_MAP[original_number] is None:
                        continue

                    # Get new task number
                    new_task_number = TASK_RENUMBERING_MAP[original_number]
                    original_task_name = f"Task{original_number}"
                    new_task_name = f"Task{new_task_number}"

                    # Create paths for the new task
                    new_task_folder = os.path.join(TASKS_FOLDER, new_task_name)
                    new_task_filename = f"{subject_id}_{new_task_name}.png"
                    new_task_filepath = os.path.join(new_task_folder, new_task_filename)

                    # Check if the original task exists or is missing
                    if original_task_name in original_task_to_path:
                        # Task exists - copy, crop, and resize the image
                        original_image_path = original_task_to_path[original_task_name]
                        crop_and_resize_image(original_image_path, new_task_filepath)
                    else:
                        # Task is missing - create a white image
                        # print(f"Missing task for {subject_id}: {original_task_name} -> {new_task_name}")
                        img_white = create_white_image()
                        cv2.imwrite(new_task_filepath, img_white)

                # Log missing tasks
                if missing_tasks:
                    with open(MISSING_TASKS_FILE, "a") as f:
                        f.write(f"{subject_folder_code}:\n")
                        f.write(f"{missing_tasks}\n")

                # Rename the subject folder to use the ID code
                if subject_folder_code != subject_id:
                    new_subject_path = os.path.join(SUBJECT_FOLDER, subject_id)

                    # If the destination already exists, merge the contents
                    if os.path.exists(new_subject_path):
                        print(f"Warning: Destination folder {subject_id} already exists. Merging contents.")
                        # Copy contents instead of renaming
                        for item in os.listdir(subject_path):
                            src_item = os.path.join(subject_path, item)
                            dst_item = os.path.join(new_subject_path, item)

                            if os.path.isdir(src_item):
                                if not os.path.exists(dst_item):
                                    os.makedirs(dst_item)
                                for file in os.listdir(src_item):
                                    src_file = os.path.join(src_item, file)
                                    dst_file = os.path.join(dst_item, file)
                                    if not os.path.exists(dst_file):
                                        os.rename(src_file, dst_file)
                            elif not os.path.exists(dst_item):
                                os.rename(src_item, dst_item)
                    else:
                        # Simple rename if destination doesn't exist
                        os.rename(subject_path, new_subject_path)

            except Exception as e:
                print(f"Error processing subject {subject_folder_code}: {e}")

            bar()

    print("\nProcessing complete!")
    return 0


if __name__ == '__main__':
    main()