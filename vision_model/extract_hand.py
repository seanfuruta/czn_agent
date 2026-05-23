import cv2
import os
import time

def extract_frames(video_path, output_folder):
    # 1. Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # 2. Open the video file
    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    frame_count = 0
    print("Starting frame extraction...")

    # 3. Loop through the video frame-by-frame
    while True:
        ret, frame = cap.read()
        
        # If ret is False, the video has reached the end or failed to read
        if not ret:
            break
            
        # 4. Generate a padded filename (e.g., frame_000001.jpg)
        # Padding with zeros keeps your files perfectly sorted alphabetically
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
        
        # 5. Save the frame to disk
        cv2.imwrite(frame_filename, frame)
        
        frame_count += 1
        
        # Optional: Print progress every 100 frames so you know it's working
        if frame_count % 100 == 0:
            print(f"Extracted {frame_count} frames...")

    # 6. Release the video capture object when done
    cap.release()
    print(f"Finished! Total frames extracted: {frame_count}")



Y_MIN, Y_MAX = 750, 1000  
X_MIN, X_MAX = 250, 850


output_dir = "data/extracted_frames"
print('hello')
print(os.getcwd())
print(os.listdir('data/raw_videos'))


raw_video_dir = r"data\raw_videos"
output_dir = "data/extracted_frames"

for video in os.listdir(raw_video_dir):
    # Glue the directory path to the filename to create a valid path
    full_video_path = os.path.join(raw_video_dir, video)
    
    # Run the extraction on the verified path
    extract_frames(full_video_path, output_dir)
    # img = cv2.imread(os.path.join(raw_frames_dir, frame_name))
    
    # # Slice the Region of Interest (ROI)
    # cropped_hand = img[Y_MIN:Y_MAX, X_MIN:X_MAX]
    # cv2.imshow("Cropped Hand", cropped_hand)
    # cv2.waitKey(0)
    # time.sleep(10000)
    # break
    # cv2.imwrite(os.path.join(output_dir, frame_name), cropped_hand)