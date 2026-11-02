
import cv2
import mediapipe as mp
import time
import numpy as np
import os

from image_capture import ImageCapture
from image_stylization import ImageStylization


# MEDIAPIPE SETUP
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2
)


# OPEN WEBCAM
camera = cv2.VideoCapture(0, cv2.CAP_MSMF)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not camera.isOpened():
    print("Camera could not open.")
    exit()


# INITIALIZE CLASSES
photo_capture = ImageCapture()
stylizer = ImageStylization()

os.makedirs("generated_images", exist_ok=True)

last_capture_time = 0
capture_cooldown = 2

captured_photo = None
preview_photo = None

styles = {
    "1": "cartoon",
    "2": "sketch",
    "3": "watercolor",
    "4": "oil",
    "0": "original"
}


# HAND CONNECTIONS
connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


print("HandFrame AI Started")
print("Show both hands to create your frame.")
print("Pinch with either hand to capture.")
print("1 = Cartoon")
print("2 = Pencil Sketch")
print("3 = Watercolor")
print("4 = Oil Painting")
print("0 = Original Photo")
print("S = Save Selected Image")
print("Q = Exit")


with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = camera.read()

        if not success:
            print("Unable to read webcam.")
            break

        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = time.monotonic_ns() // 1_000_000

        results = landmarker.detect_for_video(
            mp_image, timestamp
        )

        hands = []
        pinch_detected = False

        # DETECT HANDS
        if results.hand_landmarks:

            for landmarks in results.hand_landmarks:

                for point in landmarks:

                    x = int(point.x * width)
                    y = int(point.y * height)

                    cv2.circle(
                        frame, (x, y), 4, (0, 0, 255), -1
                    )

                for start, end in connections:

                    p1 = landmarks[start]
                    p2 = landmarks[end]

                    cv2.line(
                        frame,
                        (int(p1.x * width), int(p1.y * height)),
                        (int(p2.x * width), int(p2.y * height)),
                        (0, 255, 0),
                        2
                    )

                thumb = (
                    int(landmarks[4].x * width),
                    int(landmarks[4].y * height)
                )

                index = (
                    int(landmarks[8].x * width),
                    int(landmarks[8].y * height)
                )

                distance = np.linalg.norm(
                    np.array(thumb) - np.array(index)
                )

                if distance < 35:
                    pinch_detected = True

                    cv2.putText(
                        frame,
                        "PINCH DETECTED",
                        (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                wrist_x = int(landmarks[0].x * width)

                hands.append({
                    "wrist_x": wrist_x,
                    "thumb": thumb,
                    "index": index
                })

        # CREATE VIRTUAL FRAME
        if len(hands) == 2:

            hands.sort(key=lambda hand: hand["wrist_x"])

            left_hand = hands[0]
            right_hand = hands[1]

            corners = np.array([
                left_hand["index"],
                right_hand["index"],
                right_hand["thumb"],
                left_hand["thumb"]
            ], dtype=np.int32)

            cv2.polylines(
                frame,
                [corners],
                True,
                (255, 255, 255),
                3
            )

            for point in corners:

                cv2.circle(
                    frame,
                    tuple(point),
                    8,
                    (0, 255, 255),
                    -1
                )

            cv2.putText(
                frame,
                "HAND FRAME ACTIVE",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # CAPTURE PHOTO
            if pinch_detected:

                current_time = time.time()

                if current_time - last_capture_time >= capture_cooldown:

                    image_path = photo_capture.capture_photo(frame)

                    if image_path is not None:

                        captured_photo = cv2.imread(image_path)

                        if captured_photo is not None:
                            preview_photo = captured_photo.copy()

                    last_capture_time = current_time

        else:

            cv2.putText(
                frame,
                "Show BOTH hands to create your frame",
                (15, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

        # DISPLAY HAND COUNT
        cv2.putText(
            frame,
            f"Hands Detected: {len(hands)}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # KEYBOARD INSTRUCTIONS
        cv2.putText(
            frame,
            "1 Cartoon | 2 Sketch | 3 Watercolor | 4 Oil | 0 Original | S Save",
            (10, height - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (255, 255, 255),
            1
        )

        # DISPLAY CAPTURED PHOTO
        if preview_photo is not None:

            preview = cv2.resize(
                preview_photo,
                (640, 480)
            )

            cv2.imshow("Captured Photo Preview", preview)

        # DISPLAY WEBCAM
        cv2.imshow("HandFrame AI", frame)

        # KEYBOARD CONTROLS
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key in [ord("0"), ord("1"), ord("2"), ord("3"), ord("4")]:

            selected_style = styles[chr(key)]

            if captured_photo is not None:

                if selected_style == "original":
                    preview_photo = captured_photo.copy()

                else:
                    try:
                        preview_photo = stylizer.apply_effect(
                            captured_photo,
                            selected_style
                        )

                    except Exception as error:
                        print("Effect error:", error)

                print("Selected effect:", selected_style)

            else:
                print("Please capture a photo first!")

        # SAVE SELECTED IMAGE
        elif key in [ord("s"), ord("S")]:

            if preview_photo is not None:

                filename = time.strftime(
                    "HandFrame_Styled_%Y%m%d_%H%M%S"
                ) + ".jpg"

                save_path = os.path.join(
                    "generated_images",
                    filename
                )

                save_success = cv2.imwrite(
                    save_path,
                    preview_photo
                )

                if save_success:
                    print("Image saved successfully!")
                    print("Location:", os.path.abspath(save_path))

                else:
                    print("Unable to save image.")

            else:
                print("Please capture a photo before saving!")


camera.release()
cv2.destroyAllWindows()

print("HandFrame AI Closed")
