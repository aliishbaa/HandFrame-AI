import cv2
import os
from datetime import datetime


class ImageCapture:

    def __init__(self):
        self.save_folder = "captured_images"
        os.makedirs(self.save_folder, exist_ok=True)

    def capture_photo(self, frame):

        filename = datetime.now().strftime(
            "HandFrame_%Y%m%d_%H%M%S_%f.jpg"
        )

        image_path = os.path.join(
            self.save_folder,
            filename
        )

        success = cv2.imwrite(image_path, frame)

        if success:
            print("Photo captured successfully!")
            print("Saved at:", image_path)
            return image_path

        print("Photo could not be saved.")
        return None