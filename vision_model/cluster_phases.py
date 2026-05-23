import cv2
import os
import shutil
import numpy as np

def calculate_frame_difference(img1, img2):
    # Convert frames to grayscale for speed and accuracy
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Calculate absolute difference between the two frame matrices
    diff = cv2.absdiff(gray1, gray2)
    mean_diff = np.mean(diff)
    return mean_diff

def group_sequential_frames(input_folder, output_parent_folder, threshold=15.0):
    if not os.path.exists(output_parent_folder):
        os.makedirs(output_parent_folder)

    # Get a perfectly sorted list of frames
    frames = sorted([f for f in os.listdir(input_folder) if f.endswith(('.jpg', '.png'))])
    if not frames:
        print("No frames found!")
        return

    group_id = 0
    current_group_dir = os.path.join(output_parent_folder, f"group_{group_id:03d}")
    os.makedirs(current_group_dir, exist_ok=True)

    # Copy the absolute first frame into Group 0
    shutil.copy(os.path.join(input_folder, frames[0]), current_group_dir)
    
    prev_img = cv2.imread(os.path.join(input_folder, frames[0]))

    print("Analyzing sequential frame states...")
    for i in range(1, len(frames)):
        curr_frame_name = frames[i]
        curr_img = cv2.imread(os.path.join(input_folder, curr_frame_name))

        # Check visual delta
        diff_score = calculate_frame_difference(prev_img, curr_img)

        # If the visual difference spikes, create a new cluster group
        if diff_score > threshold:
            group_id += 1
            current_group_dir = os.path.join(output_parent_folder, f"group_{group_id:03d}")
            os.makedirs(current_group_dir, exist_ok=True)
            print(f"🎬 Scene cut detected at {curr_frame_name}! Starting Group {group_id}")

        # Move the frame into the active group folder
        shutil.copy(os.path.join(input_folder, curr_frame_name), current_group_dir)
        prev_img = curr_img

    print(f"Done! Created {group_id + 1} sequential state groups.")

# --- Execution ---
RAW_FRAMES = "data/extracted_frames"
CLUSTERED_OUTPUT = "data/grouped_phases"

# Note: You may need to tweak the threshold (e.g., 10 to 25) depending on how flashy your screen transitions are
group_sequential_frames(RAW_FRAMES, CLUSTERED_OUTPUT, threshold=20.0)