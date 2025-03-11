import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
from PIL import Image
from io import BytesIO

def compress_pdf(input_path, output_path, quality=85, render_scale=2.5):
    # 打开原始 PDF 文档
    doc = fitz.open(input_path)
    # 创建一个新文档
    new_doc = fitz.open()
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        # 使用 render_scale 提高渲染分辨率
        pix = page.get_pixmap(matrix=fitz.Matrix(render_scale, render_scale))
        
        # 利用 PIL 将 pixmap 转换为图片对象
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        if mode == "RGBA":
            img = img.convert("RGB")
        
        # 保存为 JPEG 到内存缓冲区，指定 85% 压缩质量
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
        img_bytes = img_buffer.getvalue()

        # 新页面尺寸采用原始页面尺寸，保证 PDF 页面大小不变
        rect = page.rect
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        # 将高分辨率图像缩放到原页面尺寸插入
        new_page.insert_image(new_page.rect, stream=img_bytes)
    
    new_doc.save(output_path)
    new_doc.close()
    doc.close()

def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        output_path = os.path.join(os.path.expanduser("~"), "Desktop", "compressed.pdf")
        progress_label.config(text="正在压缩，请稍候...")
        progress_bar.start()

        def run_compression():
            try:
                # 使用 quality=85 与 render_scale=2.5
                compress_pdf(file_path, output_path, quality=85, render_scale=2.5)
                progress_bar.stop()
                original_size = os.path.getsize(file_path)
                compressed_size = os.path.getsize(output_path)
                progress_label.config(text=f"压缩完成！文件已保存至：{output_path}")
                
                messagebox.showinfo(
                    "完成", 
                    f"压缩成功！\n\n原始大小: {original_size / 1024 / 1024:.2f} MB\n"
                    f"压缩后大小: {compressed_size / 1024 / 1024:.2f} MB\n"
                    f"压缩率: {(1 - compressed_size/original_size)*100:.1f}%"
                )
                root.destroy()  # 关闭 Tkinter 窗口
            except Exception as e:
                messagebox.showerror("错误", f"压缩失败：{str(e)}")

        Thread(target=run_compression).start()

# 创建 GUI 界面
root = tk.Tk()
root.title("PDF压缩工具（V1）_有问题请联系Luo")
root.geometry("400x200")

frame = tk.Frame(root)
frame.pack(pady=20)

btn_select = tk.Button(frame, text="选择PDF文件", command=select_pdf)
btn_select.pack()

progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, mode="indeterminate", length=300)
progress_bar.pack()

root.mainloop()
