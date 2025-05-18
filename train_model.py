from ultralytics import YOLO

# Khởi tạo model
model = YOLO('yolov8n-seg.pt')  # Mô hình đã được tiền huấn luyện

# Huấn luyện với các tham số hợp lệ
model.train(
    data='data.yaml',
    epochs=50,
    imgsz=640,  # Giảm kích thước ảnh để tăng tốc huấn luyện
    batch=16,  # Thay vì 'batch_size', dùng 'batch'
    device='cpu',  # Nếu không có GPU, có thể sử dụng CPU
    augment=True,  # Bật tăng cường dữ liệu
    weight_decay=0.0005,  # Thêm Weight Decay để giảm overfitting
    freeze=[0],  # Fine-tune các lớp cuối
    lr0=0.01,  # Sử dụng learning rate
)