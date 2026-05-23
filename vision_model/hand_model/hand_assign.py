import os
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Updated tag mapping using `-` for 10 and ` for non-valid hands
TAG_MAPPING = {
    '`': 'not_valid_hand',
    '0': 'valid_hand_0',
    '1': 'valid_hand_1',
    '2': 'valid_hand_2',
    '3': 'valid_hand_3',
    '4': 'valid_hand_4',
    '5': 'valid_hand_5',
    '6': 'valid_hand_6',
    '7': 'valid_hand_7',
    '8': 'valid_hand_8',
    '9': 'valid_hand_9',
    '-': 'valid_hand_10',
}

class FrameTagger:
    def __init__(self, root_dir, output_file="annotations.json"):
        self.root_dir = Path(root_dir)
        self.output_file = output_file
        self.awaiting_group_tag = False
        
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.annotations = json.load(f)
            print(f"Loaded {len(self.annotations)} existing annotations.")
        else:
            self.annotations = {}

        self.all_frames = sorted(
            [str(p) for p in self.root_dir.glob("group_*/*") if p.suffix.lower() in ['.png', '.jpg', '.jpeg']]
        )
        
        if not self.all_frames:
            print("No frames found! Check your root directory path.")
            return

        self.current_idx = 0
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.im_plot = None
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.show_frame()
        plt.show()

    def show_frame(self):
        if 0 <= self.current_idx < len(self.all_frames):
            frame_path = self.all_frames[self.current_idx]
            group_name = Path(frame_path).parent.name
            frame_name = Path(frame_path).name
            
            if frame_path not in self.annotations and self.current_idx > 0:
                prev_path = self.all_frames[self.current_idx - 1]
                if prev_path in self.annotations:
                    self.annotations[frame_path] = self.annotations[prev_path]

            current_tag = self.annotations.get(frame_path, "Unassigned")
            img = mpimg.imread(frame_path)
            
            if self.im_plot is None:
                self.im_plot = self.ax.imshow(img)
            else:
                self.im_plot.set_data(img)
            
            status_text = "AWAITING GROUP TAG (Press Shortcut Key)..." if self.awaiting_group_tag else f"Tag: {current_tag}"
            
            self.ax.set_title(
                f"Group: {group_name} | Frame: {frame_name}\n"
                f"{status_text} | [{self.current_idx + 1}/{len(self.all_frames)}]\n"
                f"Left/Right: Nav | `: Non-Valid | 0-9: Hand 0-9 | -: Hand 10\n"
                f"G + Shortcut: Tag Remainder of Group | Q: Save & Quit",
                fontsize=10
            )
            self.ax.axis('off')
            self.fig.canvas.draw_idle()

    def tag_remainder_of_group(self, shortcut_key):
        target_tag = TAG_MAPPING[shortcut_key]
        current_path = self.all_frames[self.current_idx]
        current_group = Path(current_path).parent
        
        print(f"Applying '{target_tag}' to the rest of {current_group.name}...")
        
        idx = self.current_idx
        while idx < len(self.all_frames) and Path(self.all_frames[idx]).parent == current_group:
            self.annotations[self.all_frames[idx]] = target_tag
            idx += 1
            
        self.current_idx = min(idx, len(self.all_frames) - 1)
        self.awaiting_group_tag = False
        self.show_frame()

    def save_and_quit(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)
        print(f"Progress saved to {self.output_file}. Quitting...")
        plt.close(self.fig)

    def on_key(self, event):
        if event.key == 'q':
            self.save_and_quit()
            return

        if self.awaiting_group_tag:
            if event.key in TAG_MAPPING:
                self.tag_remainder_of_group(event.key)
            else:
                print("Group tag canceled.")
                self.awaiting_group_tag = False
                self.show_frame()
            return
            
        if event.key == 'right':
            if self.current_idx < len(self.all_frames) - 1:
                self.current_idx += 1
                self.show_frame()
                
        elif event.key == 'left':
            if self.current_idx > 0:
                self.current_idx -= 1
                self.show_frame()
                
        elif event.key in TAG_MAPPING:
            frame_path = self.all_frames[self.current_idx]
            self.annotations[frame_path] = TAG_MAPPING[event.key]
            if self.current_idx < len(self.all_frames) - 1:
                self.current_idx += 1
            self.show_frame()
            
        elif event.key.lower() == 'g':
            self.awaiting_group_tag = True
            self.show_frame()

# Usage Example:
Tagger = FrameTagger(root_dir='data/grouped_phases')