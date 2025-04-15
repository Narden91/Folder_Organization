import os
import cv2
import re

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


def get_images_in_folder(images_folder_path: str, image_extension: str = ".png") -> list:
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


def crop_and_resize_image(source_path: str, destination_path: str) -> None:
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