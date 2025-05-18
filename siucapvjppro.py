import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
from ultralytics import YOLO
import os
from tkinter import ttk
import tkinter.font as tkfont
import pandas as pd
import webbrowser
import tkinter.messagebox as messagebox
import urllib.parse
import pygame

# Hàm phát nhạc nền
def play_background_music():
    pygame.mixer.init()
    pygame.mixer.music.load("BTS 방탄소년단 소우주Mikrokosmos Orchestral cover.mp3")  # Đường dẫn tới file nhạc của bạn
    pygame.mixer.music.play(-1)  # -1 để phát liên tục
    pygame.mixer.music.set_volume(0.5)  # Đặt âm lượng (0.0 đến 1.0)

# Hàm bật/tắt nhạc nền
def toggle_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

# Load YOLO model
model = YOLO("runs/segment/train2/weights/best.pt")

# Đọc file CSV
df = pd.read_csv("data/AI Final - Trang tính1.csv")

# Làm sạch tên cột (bỏ khoảng trắng thừa)
df.columns = [col.strip() for col in df.columns]

# Tạo danh sách dữ liệu bệnh viện
clinic_data = [
    {
        "hospital": row["Name"].strip(),
        "city": row["Province"].strip(),
        "address": row["Address"].strip()
    }
    for _, row in df.iterrows()
]

# Load the CSV file
csv_file = "data/Skincare_products2.csv"
products_df = pd.read_csv(csv_file, delimiter=';')

# Fill missing values in 'Skin types' and 'Products' columns
products_df['Skin types'] = products_df['Skin types'].fillna(method='ffill')
products_df['Products'] = products_df['Products'].fillna(method='ffill')

# Correct misspelled values
products_df['Products'] = products_df['Products'].replace('Exxfoliant', 'Exfoliant')

# Trim leading and trailing spaces
products_df['Skin types'] = products_df['Skin types'].str.strip()
products_df['Products'] = products_df['Products'].str.strip()

# Save the cleaned CSV file
products_df.to_csv("data/Skincare_products_cleaned.csv", index=False, sep=';')
print("CSV file cleaned and saved as 'Skincare_products_cleaned.csv'")

def create_image_with_background(image_path, bg_color="#fcf6d0"):
    # Mở ảnh với nền trong suốt (PNG)
    img = Image.open(image_path).convert("RGBA")

    # Tạo nền mới với màu #fcf6d0 và cùng kích thước với ảnh gốc
    background = Image.new("RGBA", img.size, bg_color)
    
    # Ghép ảnh lên nền mới
    combined = Image.alpha_composite(background, img)

    # Đổi sang RGB nếu muốn loại bỏ kênh alpha
    combined = combined.convert("RGB")

    return combined

def open_product_link(link):
    if pd.notna(link) and link.strip():
        webbrowser.open(link)
    else:
        messagebox.showinfo("Announce", "Product's link hasn't been updated yet.")

def show_products(skin_type, product_type):
    if not skin_type or not product_type or skin_type == "Choose your skin type" or product_type == "Choose product":
        messagebox.showwarning("Warning", "Please select both skin type and product type completely.")
        return

    skin_type = skin_type.strip().lower()
    product_type = product_type.strip().lower()

    products_df['Skin types'] = products_df['Skin types'].str.strip().str.lower()
    products_df['Products'] = products_df['Products'].str.strip().str.lower()

    filtered_products = products_df[
        (products_df['Skin types'] == skin_type) & (products_df['Products'] == product_type)
    ]

    for widget in product_frame.winfo_children():
        widget.destroy()

    product_frame.config(bg="#fcf6d0")

    def open_link(link):
        if link:
            open_product_link(link)

    # Nếu là sản phẩm Acne Treatment thì hiển thị dòng chữ cảnh báo trên cùng
    if product_type == "acne treatment":
        warning_label = tk.Label(
            product_frame, 
            text="Please consult a doctor for professional advice.", 
            fg="#ff5555",  # Màu đỏ nổi bật
            bg="#fcf6d0", 
            font=("Helvetica", 18, "italic")
        )
        warning_label.grid(row=0, column=0, columnspan=3, pady=(10, 15),)

    if filtered_products.empty:
        if product_type == "acne treatment":
            find_clinic_button = tk.Button(
                product_frame,
                text="Find nearest clinic",
                font=("Helvetica", 16, "bold"),
                fg="#bd93d8",
                bg="white",
                activebackground="#a37fcc",
                activeforeground="white",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=open_clinic_finder
            )
            find_clinic_button.grid(row=1, column=1, pady=20)
        else:
            no_product_label = tk.Label(
                product_frame,
                text="No suitable products found.",
                fg="#bd93d8",
                bg="#fcf6d0",
                font=("Helvetica", 18)
            )
            no_product_label.grid(row=1, column=0, columnspan=3)
        return

    # Bắt đầu hiển thị sản phẩm từ dòng 1 (nếu có cảnh báo) hoặc 0 (nếu không)
    start_row = 1 if product_type == "acne treatment" else 0

    for index, row in filtered_products.head(3).iterrows():
        if pd.isna(row['Image path']):
            print(f"Missing image for product: {row['Product name']}")
            continue

        img = create_image_with_background(row['Image path'], "#fcf6d0").resize((350, 300))
        img_tk = ImageTk.PhotoImage(img)

        img_label = tk.Label(product_frame, image=img_tk, cursor="hand2", bd=0, bg="#f3e6d0")
        img_label.image = img_tk
        img_label.bind("<Button-1>", lambda e, link=row.get('Product link', ''): open_link(link))
        img_label.grid(row=start_row, column=index, padx=10, pady=5)

        name_label = tk.Label(product_frame, text=row['Product name'], fg="#bd93d8", bg="#fcf6d0", cursor="hand2", font=("Helvetica", 25), wraplength=300)
        name_label.bind("<Button-1>", lambda e, link=row.get('Product link', ''): open_link(link))
        name_label.grid(row=start_row + 1, column=index, padx=20, pady=20)

# Hàm nút Start
def start_app():
    skin_check_screen()

#Hàm nút Our team
def open_team():
    our_team_screen()

# Hàm nút Result
def result_button():
    result_screen()

# Hàm nút Discover
def discover_button():
    skincare_screen()

# Hàm nút Next
def next_button():
    next_skincare_screen()

# Hàm nút Return
def return_button():
    skincare_screen()

# Hàm nút Product
def product_button():
    skince_product_screen()

# Hàm nút Routine
def routine_button():
    skincare_screen()

# Hàm nút Info
def info_button():
    skin_type_screen()

# Hàm nút find nearest clinic
def open_clinic_finder():
    clinic_screen()

# Hàm hover cho nút Start
def on_start_hover(event):
    start_label.config(image=start_hover_photo)
    start_label.image = start_hover_photo  # Giữ tham chiếu để ảnh không bị xóa

def on_start_leave(event):
    start_label.config(image=start_photo)
    start_label.image = start_photo  # Giữ lại ảnh gốc

# Hàm Back to skin check screen
def back_skin_check_screen():
    skin_check_screen()

# Hàm Back to preview screen
def back_preview_screen():
    image_path = getattr(root, "image_path", None)  # Retrieve the stored image path
    if image_path:
        preview_screen(image_path)  # Pass the image path to the preview screen
    else:
        print("No image path found to return to the preview screen.")

# Hàm Back to skincare screen
def back_result_screen():
    result_screen()

# Hàm Back to skincare screen
def back_skince_product_screen():
    skince_product_screen()

# Hàm up file ảnh
def upload_image():
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    if file_path:
        print("Đường dẫn ảnh đã chọn:", file_path)
        preview_screen(file_path)  # Chuyển sang màn hình preview và truyền ảnh

#Hàm mở camera
def open_camera():
    cap = cv2.VideoCapture(0)  # 0 là camera mặc định máy tính
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camera - Press Enter to capture", frame)
        key = cv2.waitKey(1)

        if key == 13:  # Enter
            cv2.imwrite("captured.jpg", frame)  # Lưu ảnh
            break
        elif key == ord('q'):  # Bấm q để thoát mà không chụp
            frame = None
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame is not None:
        preview_screen("captured.jpg")  # Chuyển sang màn hình preview với ảnh vừa chụp

# Màn hình chính
def main_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/SKINGENIE.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)  # Đặt ảnh phủ hết cửa sổ
    bg_label.image = bg_image_tk  # Giữ tham chiếu ảnh để tránh bị xóa

    # Nút "Our team"
    global our_team_label, our_team_photo
    our_team_img = Image.open("images/our_team.png")
    our_team_photo = ImageTk.PhotoImage(our_team_img)
    our_team_label = tk.Label(root, image=our_team_photo, bg="#ab73c0", cursor="hand")
    our_team_label.image = our_team_photo
    our_team_label.place(x=1210, y=14)
    # Gắn sự kiện click
    our_team_label.bind("<Button-1>", lambda e: open_team())

    # Nút START
    global start_label, start_photo, start_hover_photo
    start_img = Image.open("images/start.png")
    start_hover_img = Image.open("images/start_hover.png")
    start_photo = ImageTk.PhotoImage(start_img)
    start_hover_photo = ImageTk.PhotoImage(start_hover_img)
    start_label = tk.Label(root, image=start_photo, bg="white", cursor="hand")
    start_label.image = start_photo
    start_label.place(x=740, y=380)
    # Gắn click và hover
    start_label.bind("<Button-1>", lambda e: start_app())
    start_label.bind("<Enter>", on_start_hover)
    start_label.bind("<Leave>", on_start_leave)

    # Nút Toggle Music
    style = ttk.Style()
    style.theme_use('clam')  # 'clam' cho phép đổi màu nền
    style.configure('Custom.TButton',
        background='#ab73c0',
        foreground='white',
        font=('Helvetica', 16, 'bold'),
        borderwidth=0,
        focusthickness=0
    )

    toggle_music_button = ttk.Button(
        root,
        text="Music",
        style='Custom.TButton',
        command=toggle_music
    )
    toggle_music_button.place(x=1270, y=130)

# Màn hình our team
def our_team_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/team.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)  # Đặt ảnh phủ hết cửa sổ
    bg_label.image = bg_image_tk  # Giữ tham chiếu ảnh để tránh bị xóa

    # Nút "Home"
    home_img = Image.open("images/home.png")  # Bạn cần có ảnh mũi tên/quay về
    home_img = home_img.resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.image = home_photo
    home_label.place(x=7, y=734)
    # Gắn sự kiện click quay lại màn hình chính
    home_label.bind("<Button-1>", lambda e: main_screen())

# Màn hình skin check
def skin_check_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/skin_check.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)  # Đặt ảnh phủ hết cửa sổ
    bg_label.image = bg_image_tk  # Giữ tham chiếu ảnh để tránh bị xóa

    # Nút "Home"
    home_img = Image.open("images/home.png")  # Bạn cần có ảnh mũi tên/quay về
    home_img = home_img.resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.image = home_photo
    home_label.place(x=7, y=734)
    # Gắn sự kiện click quay lại màn hình chính
    home_label.bind("<Button-1>", lambda e: main_screen())

    # Nút "Upload image"
    upload_image_img = Image.open("images/upload_image.png")
    upload_image_img = upload_image_img.resize((416, 130), Image.Resampling.LANCZOS)
    upload_image_photo = ImageTk.PhotoImage(upload_image_img)
    upload_image_label = tk.Label(root, image=upload_image_photo, bg="white", cursor="hand")
    upload_image_label.image = upload_image_photo
    upload_image_label.place(x=110, y=370)
    # Gắn sự kiện click quay lại màn hình chính
    upload_image_label.bind("<Button-1>", lambda e: upload_image())

    # Nút "Take picture"
    take_picture_img = Image.open("images/take_picture.png")
    take_picture_img = take_picture_img.resize((416, 130), Image.Resampling.LANCZOS)
    take_picture_photo = ImageTk.PhotoImage(take_picture_img)
    take_picture_label = tk.Label(root, image=take_picture_photo, bg="white", cursor="hand")
    take_picture_label.image = take_picture_photo
    take_picture_label.place(x=870, y=370)
    # Gắn sự kiện click bật cam
    take_picture_label.bind("<Button-1>", lambda e: open_camera())

# Màn hình preview
def preview_screen(image_path):
    root.image_path = image_path
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/preview.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image_tk

    # Hiển thị ảnh vừa upload nếu có
    if image_path:
        try:
            user_image = Image.open(image_path)
            user_image = user_image.resize((970, 570), Image.Resampling.LANCZOS)
            user_photo = ImageTk.PhotoImage(user_image)
            img_label = tk.Label(root, image=user_photo, bg="white")
            img_label.image = user_photo
            img_label.place(x=23, y=135)  # Vị trí hiển thị ảnh trên preview
        except Exception as e:
            print("Lỗi hiển thị ảnh:", e)

    # Nút "Home"
    home_img = Image.open("images/home.png")  # Bạn cần có ảnh mũi tên/quay về
    home_img = home_img.resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.image = home_photo
    home_label.place(x=7, y=734)
    # Gắn sự kiện click quay lại màn hình chính
    home_label.bind("<Button-1>", lambda e: main_screen())

    # Nút "Back"
    back_img = Image.open("images/back.png")
    back_img = back_img.resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.image = back_photo
    back_label.place(x=1320, y=740)
    # Gắn sự kiện click quay lại trước
    back_label.bind("<Button-1>", lambda e: back_skin_check_screen())

    # Nút "Upload image AGAIN"
    upload_image_again_img = Image.open("images/upload_image_again.png")
    upload_image_again_img = upload_image_again_img.resize((380, 170), Image.Resampling.LANCZOS)
    upload_image_again_photo = ImageTk.PhotoImage(upload_image_again_img)
    upload_image_again_label = tk.Label(root, image=upload_image_again_photo, bg="white", cursor="hand")
    upload_image_again_label.image = upload_image_again_photo
    upload_image_again_label.place(x=1000, y=370)
    # Gắn sự kiện click up file ảnh
    upload_image_again_label.bind("<Button-1>", lambda e: upload_image())

    # Nút "Take picture AGAIN"
    take_picture_again_img = Image.open("images/take_picture_again.png")
    take_picture_again_img = take_picture_again_img.resize((380, 170), Image.Resampling.LANCZOS)
    take_picture_again_photo = ImageTk.PhotoImage(take_picture_again_img)
    take_picture_again_label = tk.Label(root, image=take_picture_again_photo, bg="white", cursor="hand")
    take_picture_again_label.image = take_picture_again_photo
    take_picture_again_label.place(x=1000, y=185)
    # Gắn sự kiện click quay lại màn hình chính
    take_picture_again_label.bind("<Button-1>", lambda e: open_camera())

    # Nút "Result"
    result_button_img = Image.open("images/result_button.png")
    result_button_img = result_button_img.resize((290, 120), Image.Resampling.LANCZOS)
    result_button_photo = ImageTk.PhotoImage(result_button_img)
    result_button_label = tk.Label(root, image=result_button_photo, bg="white", cursor="hand")
    result_button_label.image = result_button_photo
    result_button_label.place(x=1050, y=590)
    # Gắn sự kiện click up file ảnh
    result_button_label.bind("<Button-1>", lambda e: result_button())

# Màn hình result
def result_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # --- Ảnh nền ---
    bg_image = Image.open("images/result.png").resize((1400, 800))
    bg_image_tk = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image_tk

    # --- Nút "Our team" ---
    global our_team_label, our_team_photo
    our_team_img = Image.open("images/our_team.png")
    our_team_photo = ImageTk.PhotoImage(our_team_img)
    our_team_label = tk.Label(root, image=our_team_photo, bg="#ab73c0", cursor="hand")
    our_team_label.place(x=1210, y=14)
    our_team_label.bind("<Button-1>", lambda e: open_team())

    # --- Nút "Home" ---
    home_img = Image.open("images/home.png").resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.place(x=7, y=734)
    home_label.image = home_photo
    home_label.bind("<Button-1>", lambda e: main_screen())

    # --- Nút "Back" ---
    back_img = Image.open("images/back.png").resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.place(x=1320, y=740)
    back_label.image = back_photo
    back_label.bind("<Button-1>", lambda e: back_preview_screen())

    # --- Kiểm tra ảnh đầu vào ---
    image_path = getattr(root, "image_path", None)
    if not image_path:
        print("No image to process.")
        return

    # --- Nhận diện với YOLO ---
    results = model(image_path)[0]
    boxes = results.boxes

    # --- Hiển thị ảnh kết quả có bounding box (KHÔNG hiện phần trăm) ---
    import cv2
    img = cv2.imread(image_path)
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label = results.names[cls]
        # Draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        # Draw label (no confidence)
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result_pil = Image.fromarray(img_rgb).resize((650, 570), Image.Resampling.LANCZOS)
    result_photo = ImageTk.PhotoImage(result_pil)
    img_label = tk.Label(root, image=result_photo, bg="white")
    img_label.image = result_photo
    img_label.place(x=23, y=135)

    # --- Phân tích nhãn YOLO ---
    try:
        acne_labels = []
        for result in results:
            for *box, conf, cls in result.boxes.data.tolist():
                label = result.names[int(cls)]
                acne_labels.append(label)

        if acne_labels:
            unique_acne = list(set(acne_labels))
            result_text = "It looks like you're having some " + ", ".join([label + "s" if not label.endswith("s") else label for label in unique_acne]) + "."
        else:
            result_text = "No acne types were detected."
    except Exception as e:
        result_text = f"Error processing results: {str(e)}"

    # --- Hiển thị kết quả ---
    result_label = tk.Label(
        root,
        text=result_text,
        font=("Roboto", 40, "bold"),  # Đổi font nếu chưa cài
        bg="#fcf6d0",
        fg="#8e44ad",
        wraplength=500,
        justify="center"
    )
    result_label.place(x=790, y=300)  # Bạn có thể điều chỉnh vị trí này

    # Nút "Discover your personalized skincare routine"
    discover_img = Image.open("images/discover.png")
    discover_img = discover_img.resize((600, 135), Image.Resampling.LANCZOS)
    discover_photo = ImageTk.PhotoImage(discover_img)
    discover_label = tk.Label(root, image=discover_photo, bg="#fcf6d0", cursor="hand")
    discover_label.image = discover_photo
    discover_label.place(x=730, y=569)
    # Gắn sự kiện click up file ảnh
    discover_label.bind("<Button-1>", lambda e: discover_button())    

# Màn hình skicare routine
def skincare_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # --- Ảnh nền ---
    bg_image = Image.open("images/Skincare.png").resize((1400, 800))
    bg_image_tk = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image_tk

    # --- Nút "Home" ---
    home_img = Image.open("images/home.png").resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.place(x=7, y=734)
    home_label.image = home_photo
    home_label.bind("<Button-1>", lambda e: main_screen())

    # --- Nút "Back" ---
    back_img = Image.open("images/back.png").resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.place(x=1320, y=740)
    back_label.image = back_photo
    back_label.bind("<Button-1>", lambda e: back_result_screen())

    # --- Nút "Next" ---
    next_img = Image.open("images/next.png").resize((70, 70), Image.Resampling.LANCZOS)
    next_photo = ImageTk.PhotoImage(next_img)
    next_label = tk.Label(root, image=next_photo, bg="#3b467e", cursor="hand")
    next_label.place(x=710, y=640)
    next_label.image = next_photo
    next_label.bind("<Button-1>", lambda e: next_button())

    # --- Nút "Products" ---
    products_img = Image.open("images/products.png").resize((330, 85), Image.Resampling.LANCZOS)
    products_photo = ImageTk.PhotoImage(products_img)
    products_label = tk.Label(root, image=products_photo, bg="white", cursor="hand")
    products_label.place(x=340, y=128)
    products_label.image = products_photo
    products_label.bind("<Button-1>", lambda e: product_button())

# Màn hình next skicare routine
def next_skincare_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # --- Ảnh nền ---
    bg_image = Image.open("images/Skincare (2).png").resize((1400, 800))
    bg_image_tk = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image_tk

    # --- Nút "Home" ---
    home_img = Image.open("images/home.png").resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.place(x=7, y=734)
    home_label.image = home_photo
    home_label.bind("<Button-1>", lambda e: main_screen())

    # --- Nút "Return" ---
    return_img = Image.open("images/return.png").resize((70, 70), Image.Resampling.LANCZOS)
    return_photo = ImageTk.PhotoImage(return_img)
    return_label = tk.Label(root, image=return_photo, bg="#3b467e", cursor="hand")
    return_label.place(x=710, y=640)
    return_label.image = return_photo
    return_label.bind("<Button-1>", lambda e: return_button())

    # --- Nút "Products" ---
    products_img = Image.open("images/products.png").resize((330, 85), Image.Resampling.LANCZOS)
    products_photo = ImageTk.PhotoImage(products_img)
    products_label = tk.Label(root, image=products_photo, bg="white", cursor="hand")
    products_label.place(x=340, y=128)
    products_label.image = products_photo
    products_label.bind("<Button-1>", lambda e: product_button())

# Màn hình skince product
def skince_product_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # --- Ảnh nền ---
    bg_image = Image.open("images/skince_product.png").resize((1400, 800))
    bg_image_tk = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image_tk

    # --- Nút "Home" ---
    home_img = Image.open("images/home.png").resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.place(x=7, y=734)
    home_label.image = home_photo
    home_label.bind("<Button-1>", lambda e: main_screen())

    # --- Nút "Back" ---
    back_img = Image.open("images/back.png").resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.place(x=1320, y=740)
    back_label.image = back_photo
    back_label.bind("<Button-1>", lambda e: back_result_screen())

    # --- Nút "Routine" ---
    routine_img = Image.open("images/routine.png").resize((290, 76), Image.Resampling.LANCZOS)
    routine_photo = ImageTk.PhotoImage(routine_img)
    routine_label = tk.Label(root, image=routine_photo, bg="white", cursor="hand")
    routine_label.place(x=50, y=137)
    routine_label.image = routine_photo
    routine_label.bind("<Button-1>", lambda e: routine_button())

    # --- Nút "?" để xem mô tả loại da ---
    info_img = Image.open("images/info.png").resize((40, 40), Image.Resampling.LANCZOS)
    info_photo = ImageTk.PhotoImage(info_img)
    info_label = tk.Label(root, image=info_photo, bg="#fcf6d0", cursor="hand")
    info_label.place(x=430, y=248)
    info_label.image = info_photo
    info_label.bind("<Button-1>", lambda e: info_button())

    # --- Nút Xem sản phẩm ---
    check_button = tk.Button(root,
                         text="Show products",
                         font=("Helvetica", 25, "bold"),
                         bg="white",            # màu nền
                         fg="#bd93d8",              # màu chữ
                         activebackground="#a37fcc",  # màu khi rê chuột
                         activeforeground="white",   # màu chữ khi rê chuột
                         bd=0,                    # bỏ viền
                         highlightthickness=0,    # bỏ đường viền khi focus
                         command=lambda: show_products(combo.get(), combo1.get()))
    check_button.place(x=900, y=252)

    # ===== Dropdown chọn loại da =====
    # Tạo style mới
    style = ttk.Style()
    style.theme_use("default")  # Dùng theme mặc định để dễ tuỳ chỉnh

    # Tạo style tên là 'Custom.TCombobox'
    style.configure("Custom.TCombobox",
                fieldbackground="#bd93d8",     # Màu nền phần hiển thị
                background="#f4e4ff",          # Màu nền khi bấm xổ xuống
                foreground="#ffffff",          # Màu chữ
                bordercolor="#4d79ff",
                borderwidth=2)

    # Combobox chọn loại da
    combo = ttk.Combobox(root, 
                     values=["Normal skin", "Dry skin", "Sensitive skin", "Combination skin", "Oily skin"],
                     width=20,
                     font=("Helvetica", 30),
                     style="Custom.TCombobox")
    combo.set("Choose your skin type")
    combo.place(x=70, y=250)

    # Combobox chọn loại sản phẩm
    combo1 = ttk.Combobox(root, 
                     values=["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen", "Makeup remover", "Exfoliant", "Face mask", "Acne treatment"],
                     width=20,
                     font=("Helvetica", 30),
                     style="Custom.TCombobox")
    combo1.set("Choose product")
    combo1.place(x=500, y=250)

    # Tạo label để hiển thị kết quả
    result_label = tk.Label(root, text="", font=("Helvetica", 20), bg="#f0f0f0")
    result_label.place(x=70, y=370)

    # Frame to display products
    global product_frame
    product_frame = tk.Frame(root)
    product_frame.place(x=150, y=300)

# Màn hình chọn loại da
def skin_type_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/skin_type.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)  # Đặt ảnh phủ hết cửa sổ
    bg_label.image = bg_image_tk  # Giữ tham chiếu ảnh để tránh bị xóa

    # Nút "Home"
    home_img = Image.open("images/home.png")  # Bạn cần có ảnh mũi tên/quay về
    home_img = home_img.resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.image = home_photo
    home_label.place(x=7, y=734)
    # Gắn sự kiện click quay lại màn hình chính
    home_label.bind("<Button-1>", lambda e: main_screen())

    # Nút "Back"
    back_img = Image.open("images/back.png")
    back_img = back_img.resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.image = back_photo
    back_label.place(x=1320, y=740)
    # Gắn sự kiện click quay lại trước
    back_label.bind("<Button-1>", lambda e: back_skince_product_screen())

# Màn hình tìm bệnh viện
def clinic_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Tải ảnh làm background
    bg_image = Image.open("images/place.png")
    bg_image = bg_image.resize((1400, 800))  # Resize cho phù hợp với màn hình
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    # Tạo một label chứa ảnh background
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(relwidth=1, relheight=1)  # Đặt ảnh phủ hết cửa sổ
    bg_label.image = bg_image_tk  # Giữ tham chiếu ảnh để tránh bị xóa

    # Nút "Home"
    home_img = Image.open("images/home.png")  # Bạn cần có ảnh mũi tên/quay về
    home_img = home_img.resize((60, 60), Image.Resampling.LANCZOS)
    home_photo = ImageTk.PhotoImage(home_img)
    home_label = tk.Label(root, image=home_photo, bg="#ab73c0", cursor="hand")
    home_label.image = home_photo
    home_label.place(x=7, y=734)
    # Gắn sự kiện click quay lại màn hình chính
    home_label.bind("<Button-1>", lambda e: main_screen())

    # Nút "Back"
    back_img = Image.open("images/back.png")
    back_img = back_img.resize((70, 50), Image.Resampling.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_img)
    back_label = tk.Label(root, image=back_photo, bg="#ab73c0", cursor="hand")
    back_label.image = back_photo
    back_label.place(x=1320, y=740)
    # Gắn sự kiện click quay lại trước
    back_label.bind("<Button-1>", lambda e: back_skince_product_screen())

    # Style cho Combobox
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox", background="#FFFFFF", foreground="#000000", font=("Arial", 14), padding=10)

    # Combobox chọn tỉnh
    cities = ["All"] + sorted(list(set([item["city"] for item in clinic_data])))
    city_var = tk.StringVar(value="All")
    city_combo = ttk.Combobox(root, textvariable=city_var, values=cities, state="readonly", width=25, font=("Arial", 14))
    city_combo.place(x=710, y=212, height=35, width=300)

    # Label và Entry để nhập vị trí hiện tại
    # Label và Entry để nhập vị trí hiện tại
    tk.Label(root, text="Your location (address or lat,lng):", font=("Arial", 12), bg="white", fg="black").place(x=500, y=250)
    location_var = tk.StringVar()
    location_entry = tk.Entry(root, textvariable=location_var, font=("Arial", 12), width=43,
                            bg="#FFFACD", fg="black", highlightthickness=0, bd=0)  # Bỏ viền và highlight
    location_entry.place(x=710, y=250)
    location_var.set("10.762622,106.660172")  # vị trí mặc định

    # Hàm cập nhật bảng
    def update_table(selected_city):
        for row in tree.get_children():
            tree.delete(row)
        for item in clinic_data:
            if selected_city == "All" or item["city"] == selected_city:
                tree.insert("", "end", values=(item["hospital"], item["city"], item["address"]))

    city_combo.bind("<<ComboboxSelected>>", lambda e: update_table(city_var.get()))

    # Bảng Treeview
    tree = ttk.Treeview(root, columns=("Hospital", "City", "Address"), show="headings")

    # Định dạng các cột
    tree.heading("Hospital", text="Clinic / Hospital")
    tree.heading("City", text="Province / City")
    tree.heading("Address", text="Address")
    tree.column("Hospital", width=250, anchor="center")
    tree.column("City", width=150, anchor="center")
    tree.column("Address", width=800, anchor="w")

    # Tạo thanh cuộn dọc
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Đặt vị trí bảng và thanh cuộn
    tree.place(x=39, y=295, width=1317, height=410)
    scrollbar.place(x=1345, y=295, height=410)

    # Sự kiện double click để mở Google Maps chỉ đường
    def on_tree_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item[0], "values")
            hospital_name = values[0]
            address = values[2]
            origin = location_var.get()

            # Mã hóa URL để tránh lỗi ký tự
            origin_encoded = urllib.parse.quote_plus(origin)
            destination_encoded = urllib.parse.quote_plus(address)

            url = f"https://www.google.com/maps/dir/?api=1&origin={origin_encoded}&destination={destination_encoded}"
            webbrowser.open(url)

    tree.bind("<Double-1>", on_tree_double_click)

    # Khởi tạo bảng với tất cả dữ liệu
    update_table("All")


if __name__ == "__main__":
    play_background_music()
root = tk.Tk()
root.title("SknGenie")
root.geometry("1400x800")
main_screen()
root.mainloop()