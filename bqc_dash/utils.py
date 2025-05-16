import os


def get_information_from_path(input_dir, path):
    """Extract information from the image path"""
    # Example: Extract subject and repetition from the path
    # Assuming the path is structured as: <input_dir>/png/<subject>/<image_name>_<repetition>.png
    parts = path.split(os.sep)
    subject = parts[-2]  # Assuming the subject is in the second last part of the path
    image_name, repetition = os.path.splitext(parts[-1])[0].rsplit("_", 1)
    return subject, image_name, repetition


def get_gif_path(input_dir, image_path):
    """
    get git path from image path
    """
    (subject, image_name, repetition) = get_information_from_path(input_dir, image_path)
    return f"{subject}.gif"
