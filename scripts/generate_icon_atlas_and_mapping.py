import json
import logging
import math
import os
from PIL import Image


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), os.path.basename(__file__) + ".log"))
file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(file_handler)


REPOSITORY_ROOT_FOLDER = os.path.dirname(os.path.dirname(__file__))

FULL_COLOUR_LEGACY_ICONS = {"mastIcon", "lidarIcon"}


def get_icon_images(icon_folder, icon_extension="png"):
    files = os.listdir(icon_folder)
    images = []

    for file in files:
        if file.endswith(icon_extension):
            filepath = os.path.join(icon_folder, file)
            img = Image.open(filepath)
            images.append(img)

    return images


def generate_icon_atlas(images, file_path, icons_in_a_row=10, spacing=10, embed_name=False):
    icon_mapping = {}

    # Assume all icons have the same height and width
    # width, height = images[0].size

    # Assume all icons have a base size of 50px
    # this can be scaled up or down using styles
    width = height = 50

    # Initialize icon atlas
    icon_atlas_width = (width * icons_in_a_row) + (spacing * (icons_in_a_row + 1))

    number_of_rows = math.ceil(len(images) / icons_in_a_row)
    icon_atlas_height = (height * number_of_rows) + (spacing * (number_of_rows + 1))

    icon_atlas = Image.new(mode="RGBA", size=(icon_atlas_width, icon_atlas_height), color=(0, 0, 0, 0))

    for i, image in enumerate(images):
        row = math.floor(i / icons_in_a_row)
        column = i % icons_in_a_row

        logger.debug("Pasting icon %s to row %s column %s", image.filename, row, column)

        image_x = spacing + (width * column) + (spacing * column)
        image_y = spacing + (height * row) + (spacing * row)

        icon_name = os.path.splitext(os.path.basename(image.filename))[0]

        image = image.resize((width, height))
        icon_atlas.paste(image, (image_x, image_y))

        is_legacy_icon = not icon_name.startswith("style_") and icon_name not in FULL_COLOUR_LEGACY_ICONS
        is_legacy_turbine_icon = icon_name == "turbineIcon"

        mask = True if is_legacy_icon else False
        anchorY = height if is_legacy_turbine_icon else height / 2

        icon_mapping[icon_name] = {
            "x": image_x,
            "y": image_y,
            "width": width,
            "height": height,
            # Set this to True if we want to change the icon colors dynamically
            # Old icons were set to be used in mask mode, so WQ adds colors to it (even though its just white)
            "mask": mask,
            "anchorY": anchorY,  # If the icon has a glyph or is not centered do 'height'
        }

    icon_atlas.save(file_path)

    return icon_mapping


def main():
    logger.info("Preparing list of icons to add to icon atlas. Accepts only png files")

    images = get_icon_images(os.path.join(REPOSITORY_ROOT_FOLDER, "assets", "icons"))
    number_of_images = len(images)

    logger.info("Adding %s icons to the icon atlas", number_of_images)
    icon_atlas_file_path = os.path.join(REPOSITORY_ROOT_FOLDER, "public", "icon_atlas.png")

    icon_mapping = generate_icon_atlas(images, icon_atlas_file_path)
    logger.info("Generated icon atlas at location %s", icon_atlas_file_path)

    icon_mapping_file_path = os.path.join(REPOSITORY_ROOT_FOLDER, "public", "icon_mapping.json")
    with open(icon_mapping_file_path, "w", encoding="utf-8") as fo:
        json.dump(icon_mapping, fo, indent=2)


if __name__ == "__main__":
    main()
