import os
import sys
import shutil
import subprocess
from pathlib import Path
from PIL import Image

# Use Pillow's Resampling enum if available (Pillow 10+), fallback to older Image.BICUBIC
BICUBIC = getattr(Image, 'Resampling', Image).BICUBIC

# ---------------------------------------------------------
# Define Paths
# ---------------------------------------------------------
WORK_DIR = Path('/home/jovyan/work')
DATA_DIR = WORK_DIR / 'data'
ZIP_URL = 'https://github.com/vision-cidis/CIDIS-dataset/archive/refs/heads/main.zip'
ZIP_PATH = DATA_DIR / 'CIDIS.zip'
CIDIS_EXTRACTED = DATA_DIR / 'CIDIS-dataset-main'
CIDIS_DIR = DATA_DIR / 'CIDIS'

TISR_DATA_DIR = WORK_DIR / 'TISR' / 'datasets'
THERMAL_SRC = CIDIS_DIR / 'dataset' / 'thermal'
VISIBLE_SRC = CIDIS_DIR / 'dataset' / 'visible'
THERMAL_DEST = TISR_DATA_DIR / 'thermal'
VISIBLE_DEST = TISR_DATA_DIR / 'visible'

def main():
    # ---------------------------------------------------------
    # 1) Run and download
    # ---------------------------------------------------------
    print("--- 1) Downloading and extracting CIDIS dataset ---")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if not CIDIS_DIR.exists():
        print(f"Downloading CIDIS.zip to {ZIP_PATH}...")
        subprocess.run(["wget", ZIP_URL, "-O", str(ZIP_PATH)], check=True)
        
        print("Unzipping CIDIS.zip...")
        subprocess.run(["unzip", "-q", str(ZIP_PATH), "-d", str(DATA_DIR)], check=True)
        
        print("Renaming folder and cleaning up...")
        shutil.move(str(CIDIS_EXTRACTED), str(CIDIS_DIR))
        ZIP_PATH.unlink() # Removes the .zip file
        print("Download and extraction complete.\n")
    else:
        print("CIDIS directory already exists. Skipping download.\n")

    # ---------------------------------------------------------
    # 2) Confirm that the download was successful
    # ---------------------------------------------------------
    print("--- 2) Confirming download ---")
    if THERMAL_SRC.exists() and VISIBLE_SRC.exists():
        print("Success: CIDIS dataset structure verified.\n")
    else:
        print("Error: Could not find expected CIDIS dataset structure!")
        sys.exit(1)

    # ---------------------------------------------------------
    # 3) Repoint the images (Symlinks)
    # ---------------------------------------------------------
    print("--- 3) Setting up symlinks ---")
    TISR_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for src, dest in [(THERMAL_SRC, THERMAL_DEST), (VISIBLE_SRC, VISIBLE_DEST)]:
        # Remove existing symlink/folder if it exists to avoid FileExistsError
        if dest.exists() or dest.is_symlink():
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
        
        # Create symlink
        dest.symlink_to(src)
        print(f"Created symlink: {dest} -> {src}")
    print()

    # ---------------------------------------------------------
    # 4) Make low-resolution versions (x4 and x8)
    # ---------------------------------------------------------
    print("--- 4) Generating Low-Resolution (LR) images ---")
    
    # Define tasks: (Source HR directory, Destination LR directory, Downscale factor)
    downsample_tasks = [
        (THERMAL_DEST / 'train', THERMAL_DEST / 'train_LR_x8', 8),
        (THERMAL_DEST / 'train', THERMAL_DEST / 'train_LR_x4', 4),
        (THERMAL_DEST / 'test',  THERMAL_DEST / 'test_LR_x8',  8),
        (THERMAL_DEST / 'val',   THERMAL_DEST / 'val_LR_x8',   8)
    ]

    for hr_dir, lr_dir, scale in downsample_tasks:
        if not hr_dir.exists():
            print(f"Skipping {hr_dir.name}: Directory does not exist.")
            continue
            
        lr_dir.mkdir(parents=True, exist_ok=True)
        files = [f for f in hr_dir.iterdir() if f.suffix.lower() == '.bmp']
        
        print(f"Processing '{hr_dir.name}' -> '{lr_dir.name}' (Downscale x{scale})")
        for i, fpath in enumerate(files):
            with Image.open(fpath) as img:
                w, h = img.size
                lr = img.resize((w // scale, h // scale), BICUBIC)
                lr.save(lr_dir / fpath.name)
            
            if i > 0 and i % 100 == 0:
                print(f"  {i}/{len(files)} done")
        print(f"  All {len(files)} images done for {lr_dir.name}\n")

    # ---------------------------------------------------------
    # 5) Summary of folders and image counts
    # ---------------------------------------------------------
    print("--- 5) Directory & Image Count Summary ---")
    
    # List of directories we expect to have files
    summary_dirs = [
        THERMAL_DEST / 'train',
        THERMAL_DEST / 'train_LR_x8',
        THERMAL_DEST / 'train_LR_x4',
        THERMAL_DEST / 'test',
        THERMAL_DEST / 'test_LR_x8',
        THERMAL_DEST / 'val',
        THERMAL_DEST / 'val_LR_x8',
        VISIBLE_DEST / 'train',
        VISIBLE_DEST / 'test',
        VISIBLE_DEST / 'val'
    ]

    print(f"{'Directory Path':<65} | {'Image Count'}")
    print("-" * 80)
    for d in summary_dirs:
        if d.exists():
            # Count any image-like files
            count = len([f for f in d.iterdir() if f.is_file() and f.suffix.lower() in ['.bmp', '.png', '.jpg']])
            print(f"{str(d):<65} | {count}")
        else:
            print(f"{str(d):<65} | FOLDER NOT FOUND")

if __name__ == '__main__':
    main()