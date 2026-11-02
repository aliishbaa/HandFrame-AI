
import cv2


class ImageStylization:

    def cartoon_effect(self, image):
        # Smooth the image
        smooth = cv2.bilateralFilter(image, 9, 250, 250)

        # Create edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)

        edges = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            9
        )

        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        return cv2.bitwise_and(smooth, edges)


    def pencil_sketch(self, image):
        gray, sketch = cv2.pencilSketch(
            image,
            sigma_s=60,
            sigma_r=0.07,
            shade_factor=0.05
        )

        return sketch


    def watercolor_effect(self, image):
        return cv2.stylization(
            image,
            sigma_s=60,
            sigma_r=0.6
        )


    def oil_painting(self, image):
        return cv2.xphoto.oilPainting(
            image,
            7,
            1
        )


    def apply_effect(self, image, style):

        if style == "cartoon":
            return self.cartoon_effect(image)

        elif style == "sketch":
            return self.pencil_sketch(image)

        elif style == "watercolor":
            return self.watercolor_effect(image)

        elif style == "oil":
            return self.oil_painting(image)

        else:
            return image.copy()
