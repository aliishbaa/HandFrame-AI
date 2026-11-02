import cv2
import math


class VirtualFrame:

    def __init__(self):
        self.x = 150
        self.y = 100
        self.width = 340
        self.height = 260

    def calculate_distance(self, point1, point2):
        return math.sqrt(
            (point2[0] - point1[0]) ** 2 +
            (point2[1] - point1[1]) ** 2
        )

    def update(self, hand1, hand2, is_pinching):
        if not is_pinching:
            return

        # Find the center between both hands
        center_x = (hand1[0] + hand2[0]) // 2
        center_y = (hand1[1] + hand2[1]) // 2

        # Calculate distance between hands
        distance = self.calculate_distance(hand1, hand2)

        # Resize the frame according to hand distance
        self.width = max(150, min(600, int(distance)))
        self.height = int(self.width * 0.75)

        # Move the frame to the center of both hands
        self.x = center_x - self.width // 2
        self.y = center_y - self.height // 2

    def draw(self, frame):
        height, width, _ = frame.shape

        # Keep frame inside webcam window
        self.x = max(0, min(self.x, width - self.width))
        self.y = max(0, min(self.y, height - self.height))

        # Draw virtual frame
        cv2.rectangle(
            frame,
            (self.x, self.y),
            (self.x + self.width, self.y + self.height),
            (255, 255, 255),
            3
        )

        cv2.putText(
            frame,
            "Virtual Frame",
            (self.x + 10, self.y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        return frame