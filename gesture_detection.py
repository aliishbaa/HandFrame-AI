
import math


# Calculate distance between two points
def calculate_distance(point1, point2):

    x1, y1 = point1
    x2, y2 = point2

    distance = math.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2
    )

    return distance


# Check whether a finger is extended
def is_finger_open(landmarks, tip, pip):

    return landmarks[tip].y < landmarks[pip].y


# Check whether the thumb is extended
def is_thumb_open(landmarks):

    wrist = (landmarks[0].x, landmarks[0].y)

    thumb_tip = (landmarks[4].x, landmarks[4].y)
    thumb_ip = (landmarks[3].x, landmarks[3].y)

    tip_distance = calculate_distance(wrist, thumb_tip)
    ip_distance = calculate_distance(wrist, thumb_ip)

    return tip_distance > ip_distance * 1.15


# Count extended fingers
def count_fingers(landmarks):

    fingers_open = [
        is_thumb_open(landmarks),
        is_finger_open(landmarks, 8, 6),
        is_finger_open(landmarks, 12, 10),
        is_finger_open(landmarks, 16, 14),
        is_finger_open(landmarks, 20, 18)
    ]

    return sum(fingers_open)


# Detect hand gesture
def detect_gesture(landmarks):

    # Get thumb and index finger positions
    thumb = (landmarks[4].x, landmarks[4].y)
    index = (landmarks[8].x, landmarks[8].y)

    # Calculate distance between thumb and index finger
    pinch_distance = calculate_distance(thumb, index)

    # Detect pinch first
    if pinch_distance < 0.05:
        return "PINCH"

    # Check four fingers
    fingers_open = [
        is_finger_open(landmarks, 8, 6),
        is_finger_open(landmarks, 12, 10),
        is_finger_open(landmarks, 16, 14),
        is_finger_open(landmarks, 20, 18)
    ]

    # Detect open palm
    if all(fingers_open):
        return "OPEN PALM"

    # Detect closed fist
    if not any(fingers_open):
        return "FIST"

    # Detect other hand positions
    return "OTHER"


# Pinch detection function for compatibility
def detect_pinch(landmarks, frame_width, frame_height):

    return detect_gesture(landmarks) == "PINCH"
