import os
import sys
import json
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import timm
from torchvision import transforms

# ==========================================================================
# 1. CUSTOM DATASET CLASS WITH DYNAMIC CROPPING & CLASS FILTERING
# ==========================================================================
class DynamicCroppedDataset(Dataset):
    def __init__(self, annotations_path, crop_config_path, transform=None):
        self.transform = transform
        
        # Load the dynamic crop box coordinates [xmin, ymin, width, height]
        with open(crop_config_path, 'r') as f:
            crop_data = json.load(f)
        x, y, w, h = crop_data["crop_box"]
        # Convert to PIL crop bounding box format: (left, upper, right, lower)
        self.crop_box = (x, y, x + w, y + h)
        
        # Load and filter annotations
        with open(annotations_path, 'r') as f:
            raw_annotations = json.load(f)
            
        valid_records = []
        unique_hand_classes = set()
        
        for frame_path, tag in raw_annotations.items():
            # Filter out non-valid hands or unassigned files
            if tag == "not_valid_hand" or tag == "Unassigned":
                continue
                
            # Extract the raw hand number string (e.g., "valid_hand_3" -> "3")
            hand_num_str = tag.split('_')[-1]
            valid_records.append((frame_path, hand_num_str))
            unique_hand_classes.add(hand_num_str)
            
        # Handle missing classes by remapping them to a tight, continuous index range
        # (e.g., if hand_2 is missing, keys ['0', '1', '3'] get remapped to indices [0, 1, 2])
        self.sorted_classes = sorted(list(unique_hand_classes), key=int)
        self.class_to_idx = {class_str: idx for idx, class_str in enumerate(self.sorted_classes)}
        
        print(f"Detected valid hand counts in dataset: {self.sorted_classes}")
        print(f"Total target class count for model head: {len(self.sorted_classes)}")
        
        # Finalize internal sample inventory
        self.samples = []
        for frame_path, hand_num_str in valid_records:
            if os.path.exists(frame_path):
                self.samples.append((frame_path, self.class_to_idx[hand_num_str]))
                
        print(f"Successfully loaded {len(self.samples)} valid cropped training samples.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # Open and crop the image dynamically on-the-fly in RAM
        with Image.open(img_path).convert('RGB') as img:
            cropped_img = img.crop(self.crop_box)
            
            if self.transform:
                cropped_img = self.transform(cropped_img)
                
        return cropped_img, label


# ==========================================================================
# 2. TRAINING ORCHESTRATION FUNCTION
# ==========================================================================
def train_czn_model_on_available_hardware():
    # Automatic Hardware Detection Logic
    if torch.cuda.is_available():
        device = torch.device('cuda')
        torch.backends.cudnn.benchmark = True
        gpu_name = torch.cuda.get_device_name(0)
        print(f"🚀 Found CUDA device! Training will accelerate using: {gpu_name}")
    else:
        device = torch.device('cpu')
        print("⚠️ CUDA GPU not found. Falling back to standard CPU training loop.")

    # Setup Data Transformations
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Instantiate Dataset
    dataset = DynamicCroppedDataset(
        annotations_path="annotations.json",
        crop_config_path="crop_config.json",
        transform=train_transform
    )
    
    if len(dataset) == 0:
        print("❌ Error: No valid training samples found. Make sure annotations.json contains valid_hand tags.")
        return

    num_output_classes = len(dataset.sorted_classes)
    
    # PIN_MEMORY speeds up data transfers from CPU host RAM straight into GPU VRAM
    use_pin_memory = True if device.type == 'cuda' else False
    
    data_loader = DataLoader(
        dataset, 
        batch_size=32,          
        shuffle=True, 
        num_workers=2,          
        pin_memory=use_pin_memory
    )
    
    # Initialize ConvNeXt architecture modifying the output features to match our dataset
    model = timm.create_model(
        'convnext_tiny.fb_in22k_ft_in1k', 
        pretrained=True, 
        num_classes=num_output_classes
    )
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-2)
    
    # Core Training Loop Block
    model.train()
    print("\nStarting model fine-tuning process...")
    
    for epoch in range(5):  
        running_loss = 0.0
        for images, labels in data_loader:
            images = images.to(device, non_blocking=use_pin_memory)
            labels = labels.to(device, non_blocking=use_pin_memory)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_loss = running_loss / len(dataset)
        print(f"Epoch {epoch + 1}/5 | Training Loss: {epoch_loss:.4f}")

    # Save Artifacts
    torch.save(model.state_dict(), "czn_card_counter.pth")
    meta_config = {"class_to_idx": dataset.class_to_idx, "sorted_classes": dataset.sorted_classes}
    with open("model_meta.json", "w") as f:
        json.dump(meta_config, f, indent=4)
    print("\nTraining completed successfully! Saved weights (czn_card_counter.pth) and labels config (model_meta.json).")

if __name__ == "__main__":
    train_czn_model_on_available_hardware()