import os
import shutil

# Define the paths
source_path = 'C:\\Users\\Emanuele\\Desktop\\Dati_CRC\\Anno_2\\Soggetti'
destination_path = 'C:\\Users\\Emanuele\\Desktop\\Task_gradimento'


def copy_and_rename_files(source, destination):
    try:
        # Check if destination folder exists, if not, create it
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Iterate over items in the source directory
        for item in os.listdir(source):
            full_path = os.path.join(source, item)
            # Check if the item is a directory and follows the naming pattern
            if os.path.isdir(full_path) and item.startswith("CRC_SUBJECT_"):
                image_path = os.path.join(full_path, "images", "Task_26.png")
                # Check if the Task_26.png exists in the folder
                if os.path.isfile(image_path):
                    new_filename = f"{item}.png"
                    destination_file_path = os.path.join(destination, new_filename)
                    # Copy and rename the file
                    shutil.copy(image_path, destination_file_path)

        return "Files copied and renamed successfully."

    except Exception as e:
        return f"An error occurred: {e}"


result = copy_and_rename_files(source_path, destination_path)
print(result)
