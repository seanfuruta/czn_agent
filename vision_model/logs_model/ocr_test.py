import cv2
import easyocr

# Initialize the Reader (English text, uses GPU automatically if available)
reader = easyocr.Reader(['en'])

# 1. Load your gameplay frame
# Replace with your actual frame file path
frame = cv2.imread('data/extracted_frames/frame_001095.jpg') 

# 2. Crop strictly to the Log Region of Interest (ROI)
# Adjust these pixel coordinates based on your video resolution
# Example coordinates for the middle-left area:
y_min, y_max = 250, 550
x_min, x_max = 140, 500
log_roi = frame[y_min:y_max, x_min:x_max]

# 3. Run the Text Detector + Recognizer
# detail=1 returns bounding boxes, text strings, and confidence scores
results = reader.readtext(log_roi, detail=1)

print("--- Detected Log Lines ---")
for (bbox, text, confidence) in results:
    if confidence < 0.50:  # Skip low-confidence artifacts / animation noise
        continue
        
    # bbox format: [[top_left], [top_right], [bottom_right], [bottom_left]]
    top_left = bbox[0]
    bottom_right = bbox[2]
    
    # Calculate the Y-midpoint of this text line for your 1D Tracking logic
    y_midpoint = y_min + (top_left[1] + bottom_right[1]) / 2
    
    print(f"Text: '{text}' | Y-Coordinate: {y_midpoint:.1f} | Conf: {confidence:.2f}")
    
    # Optional: Draw the bounding boxes on the ROI image to visually verify
    cv2.rectangle(log_roi, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 2)

# Display the cropped verification frame
cv2.imshow("Log Tracker View", log_roi)
cv2.waitKey(0)
cv2.destroyAllWindows()