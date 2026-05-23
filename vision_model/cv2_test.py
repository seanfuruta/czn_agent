import cv2
import numpy as np

print("--- Step 1: Core Library Check ---")
print(f"OpenCV Version: {cv2.__version__}")

# Create a blank black image square (300x300 pixels)
blank_image = np.zeros((300, 300, 3), dtype=np.uint8)

# Try a basic matrix operation (drawing a white line)
try:
    cv2.line(blank_image, (0, 0), (300, 300), (255, 255, 255), 3)
    print("✅ Core functions and NumPy arrays are working.")
except Exception as e:
    print(f"❌ Core function failure: {e}")

print("\n--- Step 2: Build & Codec Check ---")
build_info = cv2.getBuildInformation()

# Check if Video I/O and FFmpeg are enabled
has_ffmpeg = "FFMPEG: YES" in build_info or "ffmpeg" in build_info.lower()

if has_ffmpeg:
    print("✅ Video I/O Backend: FFmpeg support is explicitly enabled.")
else:
    print("⚠️ Warning: FFmpeg support not explicitly detected in build flags.")
    print("   If reading MP4 files fails, you may need a different binary package.")

cap = cv2.VideoCapture(0) # Tries to wake up your default integrated webcam
print(cap.isOpened())
cap.release()

import os

VIDEO_PATH = r"data\raw_videos\test.mp4"

print(f"File exists: {os.path.exists(VIDEO_PATH)}")
print(f"Python has READ permission: {os.access(VIDEO_PATH, os.R_OK)}")
import cv2

cap = cv2.VideoCapture(VIDEO_PATH, cv2.CAP_FFMPEG)
print(cap.isOpened())

frame_count = 0
print("Starting frame extraction...")

# 3. Loop through the video frame-by-frame
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
    frame_count += 1
    print(f"Frame {frame_count}")
    break
cap.release()
