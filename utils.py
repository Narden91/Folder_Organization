import os
import cv2


# Acquired Image dimensions
WIDTH_ACQUIRED = 1280
HEIGHT_ACQUIRED = 720

# Image dimensions
WIDTH_IMAGE = 1920
HEIGHT_IMAGE = 1080


def get_images_in_folder(images_folder_path: str, image_extension: str = ".png") -> list:
    """ Get the list of images in the folder
    images_folder_path: the path of the folder
    image_extension: the extension of the images
    return: the list of images in the folder """
    # Get all the images in the folder
    images_file_list = [f.path for f in os.scandir(images_folder_path) if
                        f.is_file() and f.path.endswith(image_extension)]

    # Sort by filename
    images_file_list = sorted(images_file_list, key=lambda x: len(x))

    return images_file_list


def crop_and_resize_image(source_path: str, destination_path: str) -> None:
    """
    It reads an image from the specified source path, crops it to the specified coordinates, resizes it
    to the specified dimensions, and saves it to the specified destination path

    :param source_path: The path to the image you want to crop and resize
    :type source_path: str
    :param destination_path: The path to the destination image
    :type destination_path: str
    """
    try:
        # Read the image
        img = cv2.imread(source_path)

        # Get image dimensions
        height, width, channels = img.shape

        # print(f"Width: {width} \t Height: {height} \n")

        # Crop the image to specified coordinates
        cropped = img[0:HEIGHT_ACQUIRED, 0:WIDTH_ACQUIRED]

        # Resize the cropped image to specified dimensions
        resized = cv2.resize(cropped, (WIDTH_IMAGE, HEIGHT_IMAGE))

        # Save the resized image
        cv2.imwrite(destination_path, resized)
    except FileNotFoundError:
        print(f"File {source_path} NOT found!")
