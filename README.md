
# HandFrame AI

## Project Overview

HandFrame AI is a Python-based application that uses computer vision and hand gesture recognition to create an interactive virtual photography experience.

It uses a webcam to detect hand movements and gestures. Users can create a virtual frame with their hands, capture photos using a pinch gesture, apply artistic effects, and save their edited images.

## Features

- Real-time webcam video.
- Detection of up to two hands using MediaPipe.
- Hand landmark and skeleton tracking.
- Virtual frame controlled by hand positions.
- Photo capture using a pinch gesture.
- Cartoon effect.
- Pencil Sketch effect.
- Watercolor effect.
- Oil Painting effect.
- Original image preview.
- Save edited images.
- Image gallery for captured and edited photos.
- Graphical user interface built with Tkinter.

## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Pillow
- Tkinter

## Project Structure

```text
handtracking project/
│
├── captured_images/
├── generated_images/
├── models/
│   └── hand_landmarker.task
│
├── main.py
├── gui.py
├── hand_tracking.py
├── gesture_detection.py
├── virtual_frame.py
├── image_capture.py
├── image_stylization.py
├── image_gallery.py
├── test_stylization.py
│
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Install Python

Install Python on your computer.

### 2. Open the Project

Open the project folder in Visual Studio Code.

### 3. Create a Virtual Environment

Run this command in the terminal:

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows Command Prompt:

```bash
venv\Scripts\activate.bat
```

### 5. Install Required Libraries

Run:

```bash
pip install -r requirements.txt
```

### 6. Download the MediaPipe Model

Create a folder named `models` if it does not already exist.

Run this command:

```bash
curl -L "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -o models\hand_landmarker.task```

Make sure the model file is saved inside the `models` folder.

## How to Run

Connect or enable your webcam, activate the virtual environment, and run:

```bash
python main.py
```

The HandFrame AI graphical interface will open.

## How to Use

1. Start the application.
2. Allow the application to access your webcam.
3. Show your hands in front of the camera.
4. Place both hands in view to create the virtual frame.
5. Bring your thumb and index finger together to capture a photo.
6. Select an artistic effect from the control panel.
7. Click **Save Image** to save the edited image.
8. Open **Image Gallery** to view captured and edited photos.

## Output Folders

- `captured_images`: Stores captured original photos.
- `generated_images`: Stores edited and saved photos.

## Conclusion

HandFrame AI demonstrates how computer vision and hand gesture recognition can be combined to create an interactive photography application. It provides a touch-free way to capture photos and apply different artistic effects using hand gestures.

