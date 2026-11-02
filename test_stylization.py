import cv2
from image_stylization import ImageStylization

# Load a test image
image = cv2.imread("test.jpg")

if image is None:
    print("Error: Please place an image named test.jpg in the project folder.")
    exit()

# Create stylization object
stylizer = ImageStylization()

# Apply different effects
cartoon = stylizer.apply_effect(image, "cartoon")
sketch = stylizer.apply_effect(image, "sketch")
watercolor = stylizer.apply_effect(image, "watercolor")
oil = stylizer.apply_effect(image, "oil")

# Display results
cv2.imshow("Original Image", image)
cv2.imshow("Cartoon Effect", cartoon)
cv2.imshow("Pencil Sketch", sketch)
cv2.imshow("Watercolor Effect", watercolor)
cv2.imshow("Oil Painting Effect", oil)

print("Press any key to close the windows.")

cv2.waitKey(0)
cv2.destroyAllWindows()