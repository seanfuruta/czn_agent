import os
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle

class CropBoxTuner:
    def __init__(self, root_dir, config_file="crop_config.json"):
        self.root_dir = Path(root_dir)
        self.config_file = Path(config_file)
        
        # 1. Gather all frames
        self.all_frames = sorted(
            [str(p) for p in self.root_dir.glob("group_*/*") if p.suffix.lower() in ['.png', '.jpg', '.jpeg']]
        )
        
        if not self.all_frames:
            print("No frames found! Check your directory structure.")
            return

        # 2. Initial bounding box: [xmin, ymin, width, height]
        self.box = [100, 100, 300, 300] 
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                saved_data = json.load(f)
                self.box = saved_data.get("crop_box", self.box)
            print(f"Loaded existing crop box configuration: {self.box}")

        self.current_idx = 0
        
        # --- FIX: Unbind Matplotlib default shortcuts to prevent conflicts ---
        plt.rcParams['keymap.save'] = []       # Unbinds 's'
        plt.rcParams['keymap.back'] = []       # Unbinds 'left', 'c', 'backspace'
        plt.rcParams['keymap.forward'] = []    # Unbinds 'right', 'v'
        plt.rcParams['keymap.fullscreen'] = [] # Unbinds 'f'

        # 3. Setup Matplotlib canvas
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.im_plot = None
        
        self.rect = Rectangle((self.box[0], self.box[1]), self.box[2], self.box[3], 
                              linewidth=2, edgecolor='r', facecolor='none', linestyle='--')
        self.ax.add_patch(self.rect)
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.show_frame()
        plt.show()

    def show_frame(self):
        if 0 <= self.current_idx < len(self.all_frames):
            frame_path = self.all_frames[self.current_idx]
            frame_name = Path(frame_path).name
            group_name = Path(frame_path).parent.name
            
            img = mpimg.imread(frame_path)
            if self.im_plot is None:
                self.im_plot = self.ax.imshow(img)
            else:
                self.im_plot.set_data(img)
            
            self.rect.set_xy((self.box[0], self.box[1]))
            self.rect.set_width(self.box[2])
            self.rect.set_height(self.box[3])
            
            title_text = (
                f"Group: {group_name} | Frame: {frame_name} | [{self.current_idx + 1}/{len(self.all_frames)}]\n"
                f"Box coords -> Xmin: {self.box[0]}, Ymin: {self.box[1]} | Width: {self.box[2]}, Height: {self.box[3]}\n"
                f"N / B: Next/Back Frame | Arrow Keys: Move Box | Shift + Arrow Keys: Resize Box | Q: Save & Close"
            )
            self.ax.set_title(title_text, fontsize=10, loc='left')
            self.ax.axis('on')
            self.fig.canvas.draw_idle()

    def save_and_quit(self):
        config_data = {
            "crop_box": self.box,
            "notes": "Coordinates format is [xmin, ymin, width, height]"
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Crop configuration saved to {self.config_file} -> Box: {self.box}")
        plt.close(self.fig)

    def on_key(self, event):
        key = event.key
        step = 10  # Movement step size in pixels

        if key == 'q':
            self.save_and_quit()
            return

        # ---- Frame Navigation ----
        if key == 'n':  # Next Frame
            if self.current_idx < len(self.all_frames) - 1:
                self.current_idx += 1
                self.show_frame()
        elif key == 'b':  # Back Frame
            if self.current_idx > 0:
                self.current_idx -= 1
                self.show_frame()

        # ---- Resize Bounding Box (Shift + Arrow Keys) ----
        # Matplotlib appends 'up', 'down', etc., with 'shift+' modifier
        elif key == 'shift+up':     # Contract Height
            if self.box[3] > step: self.box[3] -= step
            self.show_frame()
        elif key == 'shift+down':   # Expand Height
            self.box[3] += step
            self.show_frame()
        elif key == 'shift+left':   # Contract Width
            if self.box[2] > step: self.box[2] -= step
            self.show_frame()
        elif key == 'shift+right':  # Expand Width
            self.box[2] += step
            self.show_frame()

        # ---- Move Bounding Box (Standard Arrow Keys) ----
        elif key == 'up':           # Move Up
            self.box[1] -= step
            self.show_frame()
        elif key == 'down':         # Move Down
            self.box[1] += step
            self.show_frame()
        elif key == 'left':         # Move Left
            self.box[0] -= step
            self.show_frame()
        elif key == 'right':        # Move Right
            self.box[0] += step
            self.show_frame()

# Usage Example:d
Tuner = CropBoxTuner(root_dir='data\grouped_phases')