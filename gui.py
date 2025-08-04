import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from mpa import enhance_retinal_image, evaluate_image_quality

class ImageEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tăng cường chất lượng ảnh")
        self.root.geometry("1000x700")  # Giao diện lớn hơn để chứa ảnh

        self.image_path = None
        self.original_img = None
        self.enhanced_img = None

        # Nút chọn ảnh, tăng cường, lưu ảnh
        frame_top = tk.Frame(root)
        frame_top.pack(pady=10)
        btn_load = tk.Button(frame_top, text="Chọn ảnh đầu vào", command=self.load_image, font=("Arial", 11))
        btn_load.pack(side=tk.LEFT, padx=10)
        self.btn_enhance = tk.Button(frame_top, text="Tăng cường", command=self.enhance_image, state=tk.DISABLED, font=("Arial", 11))
        self.btn_enhance.pack(side=tk.LEFT, padx=10)
        self.btn_save = tk.Button(frame_top, text="Lưu ảnh kết quả", command=self.save_enhanced_image, state=tk.DISABLED, font=("Arial", 11))
        self.btn_save.pack(side=tk.LEFT, padx=10)

        # Chỉ số đánh giá
        frame_metrics = tk.Frame(root)
        frame_metrics.pack(pady=10, fill=tk.X)
        self.frame_orig = tk.LabelFrame(frame_metrics, text="Chỉ số ảnh gốc", font=("Arial", 12, "bold"), padx=10, pady=5)
        self.frame_orig.pack(side=tk.LEFT, padx=30, fill=tk.BOTH, expand=True)
        self.label_metrics_orig = tk.Label(self.frame_orig, text="", justify=tk.LEFT, font=("Consolas", 12))
        self.label_metrics_orig.pack()

        self.frame_enh = tk.LabelFrame(frame_metrics, text="Chỉ số ảnh tăng cường", font=("Arial", 12, "bold"), padx=10, pady=5)
        self.frame_enh.pack(side=tk.LEFT, padx=30, fill=tk.BOTH, expand=True)
        self.label_metrics_enh = tk.Label(self.frame_enh, text="Chưa có", justify=tk.LEFT, font=("Consolas", 12))
        self.label_metrics_enh.pack()

        # Hiển thị ảnh gốc và ảnh tăng cường
        frame_images = tk.Frame(root)
        frame_images.pack(pady=10, fill=tk.BOTH, expand=True)
        self.canvas_orig = tk.LabelFrame(frame_images, text="Ảnh Gốc", font=("Arial", 12, "bold"))
        self.canvas_orig.pack(side=tk.LEFT, padx=20, expand=True)
        self.label_orig_img = tk.Label(self.canvas_orig)
        self.label_orig_img.pack()

        self.canvas_enh = tk.LabelFrame(frame_images, text="Ảnh Sau Tăng cường", font=("Arial", 12, "bold"))
        self.canvas_enh.pack(side=tk.LEFT, padx=20, expand=True)
        self.label_enh_img = tk.Label(self.canvas_enh)
        self.label_enh_img.pack()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.image_path = path
            img = cv2.imread(path)
            if img is not None:
                self.original_img = img
                self.show_image(img, self.label_orig_img)
                self.btn_enhance.config(state=tk.NORMAL)
                self.btn_save.config(state=tk.DISABLED)
                # Đánh giá ảnh gốc
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                metrics = evaluate_image_quality(rgb_img)
                self.show_metrics(metrics, metrics2=None)
            else:
                messagebox.showerror("Lỗi", "Không thể đọc ảnh!")

    def enhance_image(self):
        if self.original_img is None:
            return
        # Lưu ảnh gốc ra file tạm để truyền vào hàm
        tmp_path = "temp_input.jpg"
        cv2.imwrite(tmp_path, self.original_img)
        _, enhanced = enhance_retinal_image(tmp_path, scale_factor=1.0, epochs=10, pop_size=10)
        self.enhanced_img = enhanced
        self.show_image(enhanced, self.label_enh_img)

        # Đánh giá ảnh sau tăng cường
        orig_rgb = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)
        enh_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
        metrics_orig = evaluate_image_quality(orig_rgb)
        metrics_enh = evaluate_image_quality(enh_rgb)
        self.show_metrics(metrics_orig, metrics_enh)
        self.btn_save.config(state=tk.NORMAL)

    def save_enhanced_image(self):
        if self.enhanced_img is None:
            messagebox.showerror("Lỗi", "Chưa có ảnh tăng cường để lưu.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG Image", "*.png"),
                                                            ("JPEG Image", "*.jpg *.jpeg"),
                                                            ("BMP Image", "*.bmp")])
        if save_path:
            cv2.imwrite(save_path, self.enhanced_img)
            messagebox.showinfo("Thành công", f"Đã lưu ảnh kết quả:\n{save_path}")

    def show_metrics(self, metrics1, metrics2):
        names = ["Độ sáng", "Độ tương phản", "Entropy", "Độ sắc nét"]
        text_orig = "\n".join(f"{n:<18}: {v:.4f}" for n, v in zip(names, metrics1))
        self.label_metrics_orig.config(text=text_orig)

        if metrics2:
            text_enh = "\n".join(f"{n:<18}: {v:.4f}" for n, v in zip(names, metrics2))
            self.label_metrics_enh.config(text=text_enh)
        else:
            self.label_metrics_enh.config(text="Chưa có")

    def show_image(self, img_bgr, label_widget, max_size=400):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        h, w = img_rgb.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            img_pil = img_pil.resize((int(w * scale), int(h * scale)))
        img_tk = ImageTk.PhotoImage(img_pil)
        label_widget.config(image=img_tk)
        label_widget.image = img_tk  # giữ tham chiếu

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancerApp(root)
    root.mainloop()
