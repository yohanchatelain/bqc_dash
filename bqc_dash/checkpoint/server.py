import json
from datetime import datetime
import os
import pandas as pd

from bqc_dash.logger import logger
from bqc_dash.utils import get_information_from_path


class Session:
    def __init__(
        self,
        input_dir,
        images_path,
        current_index,
        rejected_images,
        timestamp=None,
    ):
        self.input_dir = input_dir
        self.images_path = images_path
        self.rejected_images = rejected_images
        self.current_index = current_index
        self.timestamp = timestamp or datetime.now().isoformat()

    def as_dict(self):
        return {
            "timestamp": self.timestamp,
            "input_dir": self.input_dir,
            "current_index": self.current_index,
            "rejected_images": self.rejected_images,
            "images_path": self.images_path,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=data.get("timestamp"),
            input_dir=data["input_dir"],
            images_path=data["images_path"],
            current_index=data["current_index"],
            rejected_images=data["rejected_images"],
        )

    def __repr__(self):
        return f"Session(input_dir={self.input_dir}, images_path={self.images_path}, current_index={self.current_index}, rejected_images={self.rejected_images}, timestamp={self.timestamp})"

    def __str__(self):
        _str = self.as_dict().__str__()
        # Return the 1024 first characters of the string
        if len(_str) > 1024:
            _str = _str[:1024] + "..."
        return _str


def save_session(filename, session):
    with open(filename, "w") as f:
        data = session.as_dict()
        timestamp = data.get("timestamp")
        json.dump(data, f, indent=2)
    return f"Checkpoint saved [{timestamp}]"


def load_session(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return Session.from_dict(data)


def save_checkpoint(filename, images_path, rejected_images, current_index, input_dir):
    if not images_path or len(images_path) == 0:
        logger.warning("No images to save in checkpoint")
        raise Warning("No images to save in checkpoint")

    session = Session(input_dir, images_path, current_index, rejected_images)
    return save_session(filename, session)


def checkpoint_load(filename):
    content = load_session(filename)
    logger.info(f"Checkpoint [{content.timestamp}] loaded successfully")
    return content


# Function to save results


def save_results(filename, results):
    assert isinstance(results, dict), "Results should be a dictionary"

    input_dir = results.get("input_dir")
    images_path = results.get("images_path")
    rejected_images = results.get("rejected_images")

    if not images_path or len(images_path) == 0:
        logger.warning("No images to save in checkpoint")
        raise Warning("No images to save in results")

    # Generate 3 files
    # 1. JSON file with the results
    # 2. JSON file with the rejected images
    # 3. JSON file with the description of the JSON files

    if os.path.exists(filename):
        logger.warning(f"File {filename} already exists. Overwriting.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_results = []
    rejected_images_results = []

    for index, image in enumerate(images_path):
        (subject, image_name, repetition) = get_information_from_path(input_dir, image)
        rejected_image = str(index) in rejected_images
        full_info = {
            "subject": subject,
            "image_name": image_name,
            "repetition": repetition,
            "path": image,
            "rejected_images": rejected_image,
            "input_dir": input_dir,
        }

        full_results.append(full_info)

        if rejected_image:
            rejected_images_results.append(full_info)

    # Check fileanme extension
    if not filename.endswith(".json"):
        filename += ".json"

    # Save the results
    pd.DataFrame(full_results).to_json(
        filename, orient="records", lines=True, date_format="iso"
    )
    logger.info(f"Results saved to {filename}")

    # Save the rejected images
    rejected_images_filename = filename.replace(".json", "_rejected.json")
    pd.DataFrame(rejected_images_results).to_json(
        rejected_images_filename, orient="records", lines=True, date_format="iso"
    )
    logger.info(f"Rejected images saved to {rejected_images_filename}")

    # Save the description of the JSON files
    description_filename = filename.replace(".json", "_description.json")
    description = {
        "timestamp": timestamp,
        "results": rejected_images_filename,
        "images_path": filename,
    }
    pd.DataFrame([description]).to_json(
        description_filename, orient="records", lines=True, date_format="iso"
    )
    logger.info(f"Description saved to {description_filename}")
