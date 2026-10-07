from ultralytics import YOLO

# Note: Update these paths to relative paths (e.g., 'data.yaml') if running on Linux
OLD_MODEL = r"D:\SIH\pipline_1\runs\detect\underwater_plastic\yolo11n_baseline-3\weights\best.pt"
DATASET = r"D:\SIH\combined_underwater_balanced\data.yaml"

print("Loading previous garbage model...")
model = YOLO(OLD_MODEL)
print("Previous model loaded successfully.")

print("\nStarting 8-class underwater training...\n")
results = model.train(
    # Dataset
    data=DATASET,
    # Training
    epochs=50,
    imgsz=640,
    batch=16,
    # GPU
    device=0,
    # Data loading
    workers=0,
    # Save checkpoints
    save=True,
    # Validation
    val=True,
    # Augmentations
    hsv_h=0.015,
    hsv_s=0.5,
    hsv_v=0.4,
    degrees=5,
    translate=0.1,
    scale=0.5,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,
    # Output
    project=r"D:\SIH\runs",
    name="underwater_8class",
    exist_ok=True
)

print("\n==========================================")
print("TRAINING COMPLETED")
print("==========================================")
print("Best model: D:\\SIH\\runs\\underwater_8class\\weights\\best.pt")
print("Last checkpoint: D:\\SIH\\runs\\underwater_8class\\weights\\last.pt")
