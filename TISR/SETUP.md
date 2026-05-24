# TISR — Setup, Training & Testing Guide

HAT-L model fine-tuned for 8x Thermal Image Super-Resolution (PBVS 2024 Challenge).

---

## 1. Clone the Repository

```bash
git clone https://github.com/musharaff87/Practicum-Project-Intial-Run.git
cd Practicum-Project-Intial-Run/TISR
```

---

## 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install PyTorch (CUDA 11.8 recommended)

```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

> For CPU-only: `pip install torch torchvision`

---

## 4. Install Python Dependencies

```bash
pip install -r requirements.txt
python setup.py develop
```

---

## 5. Install Modified BasicSR

```bash
cd BasicSR
pip install -e .
cd ..
```

---

## 6. Install rclone (for large file downloads)

```bash
# Linux
sudo apt install rclone        # or: curl https://rclone.org/install.sh | sudo bash

# Configure with your Google Drive token
mkdir -p ~/.config/rclone
# Paste your rclone.conf here (see section 7)
```

---

## 7. Configure rclone Google Drive Remote

Create `~/.config/rclone/rclone.conf` with the following content (replace `<TOKEN_JSON>` with your token):

```ini
[gdrive-dcu]
type = drive
scope = drive
token = <TOKEN_JSON>
```

To generate a new token:
```bash
rclone config   # choose: n → drive → gdrive-dcu → follow browser auth
```

Verify connection:
```bash
rclone lsd gdrive-dcu:
```

---

## 8. Download Large Files from Google Drive

```bash
# Download everything (models + dataset)
bash scripts/gdrive_pull.sh all

# Or selectively:
bash scripts/gdrive_pull.sh models    # only model checkpoints
bash scripts/gdrive_pull.sh dataset   # only dataset
```

This places files at:
- Models: `experiments/pretrained_models/` and `experiments/Train_HAT-L_SRx8_FT_Thermal/models/`
- Dataset: `/home/jovyan/work/data/CIDIS/dataset/thermal/`

---

## 9. Dataset Structure

Expected layout after pulling:

```
/home/jovyan/work/data/CIDIS/dataset/thermal/
├── train/          # HR training images
├── train_LR_x8/    # LR training images (8x downscaled)
├── val/            # HR validation images
├── val_LR_x8/      # LR validation images
└── test_LR_x8/     # LR test images (no HR ground truth)
```

---

## 10. Training

Edit `options/train/train_HAT-L_SRx8_finetune_from_ImageNet_pretrain_datasets0.yml` to set your dataset paths, then:

```bash
# Single GPU
python hat/train.py -opt options/train/train_HAT-L_SRx8_finetune_from_ImageNet_pretrain_datasets0.yml

# Multi-GPU (e.g. 2 GPUs)
CUDA_VISIBLE_DEVICES=0,1 python -m torch.distributed.launch \
  --nproc_per_node=2 --master_port=4321 \
  hat/train.py \
  -opt options/train/train_HAT-L_SRx8_finetune_from_ImageNet_pretrain_datasets0.yml \
  --launcher pytorch
```

Training logs and checkpoints are saved to `experiments/Train_HAT-L_SRx8_FT_Thermal/`.

---

## 11. Testing

```bash
/path/to/venv/bin/python hat/test.py -opt options/test/HAT-L_SRx8_ImageNet-pretrain.yml
```

Or with the venv activated:
```bash
python hat/test.py -opt options/test/HAT-L_SRx8_ImageNet-pretrain.yml
```

Results are saved to `results/20240301_datasets_mse_ssim0.02_10000/visualization/thermal/`.

---

## 12. Pushing Large Files to Google Drive

After training new checkpoints:

```bash
bash scripts/gdrive_push.sh
```

This uploads all `.pth` / `.state` files and the dataset to `gdrive-dcu:TISR/`.

---

## 13. Key Config Files

| File | Purpose |
|------|---------|
| `options/train/train_HAT-L_SRx8_finetune_from_ImageNet_pretrain_datasets0.yml` | Training config |
| `options/test/HAT-L_SRx8_ImageNet-pretrain.yml` | Test config |
| `scripts/gdrive_push.sh` | Upload large files to GDrive |
| `scripts/gdrive_pull.sh` | Download large files from GDrive |
| `~/.config/rclone/rclone.conf` | rclone credentials (not in git) |
