import cv2
import numpy as np

def preprocess_image(image_path):
    # Step 1: Read the image
    img = cv2.imread(image_path)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 3: Remove black borders
    # Threshold the image to create a binary mask
    _, binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    # Find the bounding box of the non-black region
    coords = cv2.findNonZero(binary)  # Find all non-zero pixel coordinates
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)  # Get the bounding box
        cropped = gray[y:y+h, x:x+w]  # Crop the image to the bounding box
    else:
        cropped = gray  # If no non-black regions are found, use the original

    # Step 4: Deskew the image (rotation correction)
    coords = np.column_stack(np.where(cropped > 0))  # Get non-zero pixel coordinates
    angle = cv2.minAreaRect(coords)[-1]  # Get the angle of rotation
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotate the image to correct skew
    (h, w) = cropped.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(cropped, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Step 5: Enhance Contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(deskewed)

    # Step 6: Apply Adaptive Thresholding
    thresholded = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5
    )

    # Save the processed image
    processed_path = "static/uploads/processed_image.png"
    cv2.imwrite(processed_path, thresholded)

    return processed_path
