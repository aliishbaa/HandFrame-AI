
import tkinter as tk
from tkinter import messagebox
import cv2
import mediapipe as mp
import numpy as np
import time
import os

from datetime import datetime
from PIL import Image, ImageTk

from image_capture import ImageCapture
from image_stylization import ImageStylization
from gesture_detection import detect_gesture
from image_gallery import ImageGallery


class HandFrameAI:

    def __init__(self, root):

        self.root = root
        self.root.title("HandFrame AI | Smart Photo Editor")
        self.root.geometry("1200x850")
        self.root.minsize(1050, 760)
        self.root.configure(bg="#101827")

        self.bg_color = "#101827"
        self.panel_color = "#1B2638"
        self.blue_color = "#2878D0"
        self.text_color = "#FFFFFF"
        self.muted_color = "#AAB8CA"

        self.photo_capture = ImageCapture()
        self.stylizer = ImageStylization()

        os.makedirs("generated_images", exist_ok=True)

        self.original_photo = None
        self.preview_photo = None

        self.current_frame = None
        self.current_clean_frame = None

        # Prevent repeated capture while holding a pinch
        self.previous_pinch_state = False

        # Selected photo effect
        self.selected_effect = "Original Image"

        # Initialize webcam
        self.camera = cv2.VideoCapture(0, cv2.CAP_MSMF)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            messagebox.showerror(
                "Camera Error",
                "Could not open webcam."
            )
            self.root.destroy()
            return

        # MediaPipe setup
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

        self.landmarker = HandLandmarker.create_from_options(options)

        # Hand connections
        self.connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        self.create_interface()
        self.update_camera()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # -----------------------------------
    # CREATE INTERFACE
    # -----------------------------------

    def create_interface(self):

        header = tk.Frame(
            self.root,
            bg=self.panel_color,
            height=90
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="HANDFRAME AI",
            font=("Segoe UI", 25, "bold"),
            bg=self.panel_color,
            fg=self.text_color
        ).pack(anchor="w", padx=30, pady=(12, 0))

        tk.Label(
            header,
            text="AI-Based Hand Gesture Photo Editor",
            font=("Segoe UI", 10),
            bg=self.panel_color,
            fg=self.muted_color
        ).pack(anchor="w", padx=30)

        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        main_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=12
        )

        # Left side
        left_frame = tk.Frame(
            main_frame,
            bg=self.bg_color
        )
        left_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        # Right side
        right_frame = tk.Frame(
            main_frame,
            bg=self.panel_color,
            width=270
        )
        right_frame.pack(
            side="right",
            fill="y",
            padx=(8, 0)
        )
        right_frame.pack_propagate(False)

        # Camera section
        camera_card = tk.Frame(
            left_frame,
            bg=self.panel_color,
            padx=12,
            pady=10
        )
        camera_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            camera_card,
            text="LIVE CAMERA",
            font=("Segoe UI", 13, "bold"),
            bg=self.panel_color,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 8))

        self.camera_label = tk.Label(
            camera_card,
            bg="#080D16",
            width=600,
            height=270
        )
        self.camera_label.pack()

        tk.Label(
            camera_card,
            text="Show both hands to create your virtual frame",
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg=self.muted_color
        ).pack(anchor="w", pady=(6, 0))

        # Photo preview section
        preview_card = tk.Frame(
            left_frame,
            bg=self.panel_color,
            height=220,
            padx=12,
            pady=10
        )
        preview_card.pack(
            fill="both",
            expand=True
        )
        preview_card.pack_propagate(False)

        tk.Label(
            preview_card,
            text="PHOTO PREVIEW",
            font=("Segoe UI", 13, "bold"),
            bg=self.panel_color,
            fg=self.text_color
        ).pack(anchor="w", pady=(0, 8))

        self.photo_label = tk.Label(
            preview_card,
            text="Your captured photo will appear here",
            font=("Segoe UI", 11),
            bg="#080D16",
            fg=self.muted_color,
            anchor="center"
        )
        self.photo_label.pack(
            fill="both",
            expand=True
        )

        # Control section
        tk.Label(
            right_frame,
            text="PHOTO CONTROLS",
            font=("Segoe UI", 16, "bold"),
            bg=self.panel_color,
            fg=self.text_color
        ).pack(pady=(20, 15))

        self.section_label(right_frame, "CAPTURE")

        self.create_button(
            right_frame,
            "Capture Photo",
            self.capture_photo,
            self.blue_color
        )

        self.section_label(right_frame, "ARTISTIC EFFECTS")

        self.create_button(
            right_frame,
            "Cartoon",
            lambda: self.apply_style("cartoon")
        )

        self.create_button(
            right_frame,
            "Pencil Sketch",
            lambda: self.apply_style("sketch")
        )

        self.create_button(
            right_frame,
            "Watercolor",
            lambda: self.apply_style("watercolor")
        )

        self.create_button(
            right_frame,
            "Oil Painting",
            lambda: self.apply_style("oil")
        )

        self.create_button(
            right_frame,
            "Original Image",
            self.show_original,
            "#40516A"
        )

        self.section_label(right_frame, "SAVE YOUR WORK")

        self.create_button(
            right_frame,
            "Save Image",
            self.save_image,
            "#16845B"
        )

        # Gallery button
        self.create_button(
            right_frame,
            "Open Image Gallery",
            self.open_gallery,
            "#7255B5"
        )

        self.create_button(
            right_frame,
            "Exit Application",
            self.close_application,
            "#B83B45"
        )

        # -----------------------------------
        # STATUS BAR
        # -----------------------------------

        footer = tk.Frame(
            self.root,
            bg=self.panel_color,
            height=72
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.status_label = tk.Label(
            footer,
            text="Ready. Show your hands to begin.",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_color,
            fg="#72B7FF"
        )
        self.status_label.pack(
            anchor="w",
            padx=20,
            pady=(7, 2)
        )

        info_frame = tk.Frame(
            footer,
            bg=self.panel_color
        )
        info_frame.pack(
            fill="x",
            padx=20,
            pady=(2, 5)
        )

        self.camera_status_label = tk.Label(
            info_frame,
            text="Camera: Starting...",
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg="#72B7FF"
        )
        self.camera_status_label.pack(
            side="left",
            padx=(0, 20)
        )

        self.hands_status_label = tk.Label(
            info_frame,
            text="Hands: 0",
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg=self.text_color
        )
        self.hands_status_label.pack(
            side="left",
            padx=(0, 20)
        )

        self.gesture_status_label = tk.Label(
            info_frame,
            text="Gesture: None",
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg=self.text_color
        )
        self.gesture_status_label.pack(
            side="left",
            padx=(0, 20)
        )

        self.effect_status_label = tk.Label(
            info_frame,
            text="Effect: Original Image",
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg="#72D69B"
        )
        self.effect_status_label.pack(
            side="left"
        )

    # -----------------------------------
    # SECTION LABEL
    # -----------------------------------

    def section_label(self, parent, text):

        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self.panel_color,
            fg=self.muted_color
        ).pack(
            anchor="w",
            padx=22,
            pady=(14, 5)
        )

    # -----------------------------------
    # BUTTON DESIGN
    # -----------------------------------

    def create_button(
        self,
        parent,
        text,
        command,
        color="#30445F"
    ):

        tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="white",
            activebackground="#3D83CA",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=23,
            pady=9,
            cursor="hand2"
        ).pack(
            padx=18,
            pady=4,
            fill="x"
        )

    # -----------------------------------
    # WEBCAM AND GESTURE DETECTION
    # -----------------------------------

    def update_camera(self):

        success, frame = self.camera.read()

        if not success:

            self.status_label.config(
                text="Unable to read webcam."
            )

            self.camera_status_label.config(
                text="Camera: Disconnected",
                fg="#FF7777"
            )

            self.hands_status_label.config(
                text="Hands: 0"
            )

            self.gesture_status_label.config(
                text="Gesture: None"
            )

            self.root.after(100, self.update_camera)
            return

        self.camera_status_label.config(
            text="Camera: Connected",
            fg="#72D69B"
        )

        frame = cv2.flip(frame, 1)

        # Save clean frame before drawing graphics
        clean_frame = frame.copy()
        self.current_clean_frame = clean_frame.copy()

        height, width, _ = frame.shape

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = time.monotonic_ns() // 1_000_000

        results = self.landmarker.detect_for_video(
            mp_image,
            timestamp
        )

        hands = []
        pinch_detected = False
        gesture_names = []

        # Detect hands
        if results.hand_landmarks:

            for landmarks in results.hand_landmarks:

                gesture = detect_gesture(landmarks)
                gesture_names.append(gesture)

                # Draw landmarks
                for point in landmarks:

                    x = int(point.x * width)
                    y = int(point.y * height)

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (0, 0, 255),
                        -1
                    )

                # Draw hand skeleton
                for start, end in self.connections:

                    p1 = landmarks[start]
                    p2 = landmarks[end]

                    cv2.line(
                        frame,
                        (
                            int(p1.x * width),
                            int(p1.y * height)
                        ),
                        (
                            int(p2.x * width),
                            int(p2.y * height)
                        ),
                        (0, 255, 0),
                        2
                    )

                # Display gesture
                wrist_x = int(landmarks[0].x * width)
                wrist_y = int(landmarks[0].y * height)

                cv2.putText(
                    frame,
                    gesture,
                    (wrist_x - 20, wrist_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2
                )

                if gesture == "PINCH":
                    pinch_detected = True

                # Save hand information for virtual frame
                thumb = (
                    int(landmarks[4].x * width),
                    int(landmarks[4].y * height)
                )

                index = (
                    int(landmarks[8].x * width),
                    int(landmarks[8].y * height)
                )

                hands.append({
                    "wrist_x": wrist_x,
                    "thumb": thumb,
                    "index": index
                })

        # Update hand and gesture status
        self.hands_status_label.config(
            text=f"Hands: {len(hands)}"
        )

        if gesture_names:

            self.gesture_status_label.config(
                text="Gesture: " + " | ".join(gesture_names)
            )

        else:

            self.gesture_status_label.config(
                text="Gesture: None"
            )

        # -----------------------------------
        # NEW PINCH DETECTION
        # -----------------------------------

        current_pinch_state = (
            len(hands) == 2 and pinch_detected
        )

        new_pinch = (
            current_pinch_state
            and not self.previous_pinch_state
        )

        self.previous_pinch_state = current_pinch_state

        # -----------------------------------
        # CREATE VIRTUAL FRAME
        # -----------------------------------

        if len(hands) == 2:

            hands.sort(
                key=lambda hand: hand["wrist_x"]
            )

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

            # Capture only once for each new pinch
            if new_pinch:
                self.capture_photo()

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

        # Display hand count
        cv2.putText(
            frame,
            f"Hands Detected: {len(hands)}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Store frame with graphics for camera display
        self.current_frame = frame.copy()

        # Display webcam
        display_frame = cv2.resize(
            frame,
            (600, 270)
        )

        display_frame = cv2.cvtColor(
            display_frame,
            cv2.COLOR_BGR2RGB
        )

        camera_image = Image.fromarray(display_frame)
        camera_photo = ImageTk.PhotoImage(camera_image)

        self.camera_label.config(
            image=camera_photo
        )

        self.camera_label.image = camera_photo

        self.root.after(
            10,
            self.update_camera
        )

    # -----------------------------------
    # CAPTURE PHOTO
    # -----------------------------------

    def capture_photo(self):

        if self.current_clean_frame is None:

            self.status_label.config(
                text="Camera frame is not ready."
            )
            return

        # Save clean photo without tracking graphics
        image_path = self.photo_capture.capture_photo(
            self.current_clean_frame
        )

        if image_path is not None:

            image = cv2.imread(image_path)

            if image is not None:

                self.original_photo = image.copy()
                self.preview_photo = image.copy()

                self.selected_effect = "Original Image"

                self.effect_status_label.config(
                    text="Effect: Original Image"
                )

                self.show_photo_preview()

                self.status_label.config(
                    text="Clean photo captured successfully!"
                )

    # -----------------------------------
    # SHOW PHOTO PREVIEW
    # -----------------------------------

    def show_photo_preview(self):

        if self.preview_photo is None:
            return

        preview = cv2.cvtColor(
            self.preview_photo,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(preview)

        # Keep original image proportions
        image.thumbnail(
            (520, 175),
            Image.Resampling.LANCZOS
        )

        photo = ImageTk.PhotoImage(image)

        self.photo_label.config(
            image=photo,
            text=""
        )

        self.photo_label.image = photo

    # -----------------------------------
    # APPLY ARTISTIC EFFECTS
    # -----------------------------------

    def apply_style(self, style):

        if self.original_photo is None:

            self.status_label.config(
                text="Please capture a photo first."
            )
            return

        try:

            self.preview_photo = self.stylizer.apply_effect(
                self.original_photo,
                style
            )

            effect_names = {
                "cartoon": "Cartoon",
                "sketch": "Pencil Sketch",
                "watercolor": "Watercolor",
                "oil": "Oil Painting"
            }

            self.selected_effect = effect_names.get(
                style,
                "Original Image"
            )

            self.effect_status_label.config(
                text="Effect: " + self.selected_effect
            )

            self.show_photo_preview()

            self.status_label.config(
                text="Applied effect: " + self.selected_effect
            )

        except Exception as error:

            messagebox.showerror(
                "Effect Error",
                str(error)
            )

    # -----------------------------------
    # RESTORE ORIGINAL PHOTO
    # -----------------------------------

    def show_original(self):

        if self.original_photo is None:

            self.status_label.config(
                text="Please capture a photo first."
            )
            return

        self.preview_photo = self.original_photo.copy()
        self.selected_effect = "Original Image"

        self.effect_status_label.config(
            text="Effect: Original Image"
        )

        self.show_photo_preview()

        self.status_label.config(
            text="Original photo restored."
        )

    # -----------------------------------
    # SAVE EDITED IMAGE
    # -----------------------------------

    def save_image(self):

        if self.preview_photo is None:

            self.status_label.config(
                text="Please capture a photo first."
            )
            return

        filename = datetime.now().strftime(
            "HandFrame_Styled_%Y%m%d_%H%M%S_%f.jpg"
        )

        save_path = os.path.join(
            "generated_images",
            filename
        )

        success = cv2.imwrite(
            save_path,
            self.preview_photo
        )

        if success:

            self.status_label.config(
                text="Image saved successfully!"
            )

            print(
                "Image saved at:",
                os.path.abspath(save_path)
            )

            messagebox.showinfo(
                "Image Saved",
                "Your image was saved successfully!\n\n"
                + save_path
            )

        else:

            messagebox.showerror(
                "Save Error",
                "Could not save the image."
            )

    # -----------------------------------
    # OPEN IMAGE GALLERY
    # -----------------------------------

    def open_gallery(self):

        ImageGallery(self.root)

        self.status_label.config(
            text="Image gallery opened."
        )

    # -----------------------------------
    # CLOSE APPLICATION
    # -----------------------------------

    def close_application(self):

        if hasattr(self, "camera") and self.camera.isOpened():
            self.camera.release()

        if hasattr(self, "landmarker"):
            self.landmarker.close()

        self.root.destroy()


# -----------------------------------
# RUN APPLICATION
# -----------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = HandFrameAI(root)

    root.mainloop()
