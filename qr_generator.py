import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import os
import time

class QRGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.resizable(False, False)

        self.colors = {
            "bg": "#F0F2F5",
            "surface": "#FFFFFF",
            "primary": "#6C63FF",
            "primary_hover": "#5A52D5",
            "text": "#1A1A2E",
            "text_secondary": "#6B7280",
            "border": "#E0E0E0",
            "success": "#10B981",
            "warning_bg": "#FEF3C7",
            "warning_text": "#92400E",
        }

        self.root.configure(bg=self.colors["bg"])

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TCombobox", fieldbackground=self.colors["surface"],
                             background=self.colors["surface"],
                             foreground=self.colors["text"],
                             arrowcolor=self.colors["primary"],
                             bordercolor=self.colors["border"],
                             lightcolor=self.colors["border"],
                             darkcolor=self.colors["border"],
                             selectbackground=self.colors["primary"],
                             selectforeground="white")

        main = tk.Frame(root, bg=self.colors["bg"], padx=32, pady=28)
        main.pack(fill="both", expand=True)

        header = tk.Frame(main, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 24))

        tk.Label(header, text="QR Code Generator", font=("Segoe UI", 20, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w")
        tk.Label(header, text="Generate QR codes instantly from any URL or text",
                 font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_secondary"]).pack(anchor="w")

        body = tk.Frame(main, bg=self.colors["bg"])
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=self.colors["bg"])
        left.pack(side="left", fill="both", expand=True)

        input_card = tk.Frame(left, bg=self.colors["surface"], padx=20, pady=20,
                               highlightbackground=self.colors["border"],
                               highlightthickness=1)
        input_card.pack(fill="x")

        tk.Label(input_card, text="Enter URL or text", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["surface"], fg=self.colors["text"]).pack(anchor="w")

        entry_row = tk.Frame(input_card, bg=self.colors["surface"])
        entry_row.pack(fill="x", pady=(8, 0))

        self.entry = tk.Entry(entry_row, font=("Segoe UI", 11),
                               bg=self.colors["surface"], fg=self.colors["text"],
                               relief="solid", bd=1, highlightthickness=1,
                               highlightcolor=self.colors["primary"],
                               highlightbackground=self.colors["border"])
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
        self.entry.bind("<Return>", lambda e: self.generate())

        self.gen_btn = tk.Button(entry_row, text="Generate", font=("Segoe UI", 10, "bold"),
                                  bg=self.colors["primary"], fg="white", relief="flat", padx=24,
                                  activebackground=self.colors["primary_hover"],
                                  activeforeground="white", cursor="hand2", command=self.generate)
        self.gen_btn.pack(side="left", padx=(10, 0), ipady=7)

        options_row = tk.Frame(input_card, bg=self.colors["surface"])
        options_row.pack(fill="x", pady=(16, 0))

        err_frame = tk.Frame(options_row, bg=self.colors["surface"])
        err_frame.pack(side="left", fill="x", expand=True)
        tk.Label(err_frame, text="Error Correction", font=("Segoe UI", 9),
                 bg=self.colors["surface"], fg=self.colors["text_secondary"]).pack(anchor="w")
        self.err_combo = ttk.Combobox(err_frame, values=["L (Low)", "M (Medium)", "Q (Quartile)", "H (High)"],
                                       state="readonly", font=("Segoe UI", 10), height=4)
        self.err_combo.current(1)
        self.err_combo.pack(fill="x", pady=(4, 0), ipady=2)

        size_frame = tk.Frame(options_row, bg=self.colors["surface"])
        size_frame.pack(side="left", fill="x", expand=True, padx=(16, 0))
        tk.Label(size_frame, text="QR Size", font=("Segoe UI", 9),
                 bg=self.colors["surface"], fg=self.colors["text_secondary"]).pack(anchor="w")
        self.size_combo = ttk.Combobox(size_frame, values=["Small", "Medium", "Large"],
                                        state="readonly", font=("Segoe UI", 10), height=3)
        self.size_combo.current(1)
        self.size_combo.pack(fill="x", pady=(4, 0), ipady=2)

        self.status_bar = tk.Frame(left, bg=self.colors["bg"])
        self.status_bar.pack(fill="x", pady=(16, 0))

        self.status_icon = tk.Label(self.status_bar, text="", font=("Segoe UI", 9),
                                     bg=self.colors["bg"], fg=self.colors["text_secondary"])
        self.status_icon.pack(side="left")

        self.status_text = tk.Label(self.status_bar, text="Ready", font=("Segoe UI", 9),
                                     bg=self.colors["bg"], fg=self.colors["text_secondary"],
                                     anchor="w")
        self.status_text.pack(side="left", padx=(4, 0))

        right = tk.Frame(body, bg=self.colors["bg"])
        right.pack(side="left", fill="y", padx=(24, 0))

        preview_card = tk.Frame(right, bg=self.colors["surface"], padx=20, pady=20,
                                 highlightbackground=self.colors["border"],
                                 highlightthickness=1)
        preview_card.pack(fill="both", expand=True)

        tk.Label(preview_card, text="Preview", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["surface"], fg=self.colors["text"]).pack(anchor="w")

        self.canvas_frame = tk.Frame(preview_card, bg=self.colors["surface"], padx=8, pady=8)
        self.canvas_frame.pack(pady=(8, 0))

        self.canvas = tk.Canvas(self.canvas_frame, width=260, height=260,
                                 bg="white", highlightthickness=0)
        self.canvas.pack()
        self.placeholder = self.canvas.create_text(130, 130, text="Your QR code\nwill appear here",
                                                    fill=self.colors["text_secondary"],
                                                    font=("Segoe UI", 10), justify="center")

        action_row = tk.Frame(preview_card, bg=self.colors["surface"])
        action_row.pack(fill="x", pady=(14, 0))

        self.save_btn = tk.Button(action_row, text="Save As...", font=("Segoe UI", 10, "bold"),
                                   bg=self.colors["primary"], fg="white", relief="flat",
                                   padx=20, activebackground=self.colors["primary_hover"],
                                   activeforeground="white", cursor="hand2",
                                   state="disabled", command=self.save_as)
        self.save_btn.pack(side="left", ipady=5)

        self.copy_btn = tk.Button(action_row, text="Copy Path", font=("Segoe UI", 10),
                                   bg=self.colors["surface"], fg=self.colors["primary"],
                                   relief="solid", bd=1, padx=16,
                                   activebackground=self.colors["border"],
                                   cursor="hand2", state="disabled", command=self.copy_path)
        self.copy_btn.pack(side="left", padx=(8, 0), ipady=5)

        self.open_btn = tk.Button(action_row, text="Open Folder", font=("Segoe UI", 10),
                                   bg=self.colors["surface"], fg=self.colors["primary"],
                                   relief="solid", bd=1, padx=16,
                                   activebackground=self.colors["border"],
                                   cursor="hand2", state="disabled", command=self.open_folder)
        self.open_btn.pack(side="left", padx=(8, 0), ipady=5)

        self.path_card = tk.Frame(right, bg=self.colors["surface"], padx=16, pady=12,
                                   highlightbackground=self.colors["border"],
                                   highlightthickness=1)
        self.path_card.pack(fill="x", pady=(16, 0))

        self.path_label = tk.Label(self.path_card, text="No QR code generated yet",
                                    font=("Segoe UI", 9),
                                    bg=self.colors["surface"],
                                    fg=self.colors["text_secondary"], anchor="w",
                                    wraplength=320, justify="left")
        self.path_label.pack(fill="x")

        self.qr_image = None
        self.qr_photo = None
        self.last_saved_path = None

    def get_qr_params(self):
        err_map = {
            "L (Low)": qrcode.constants.ERROR_CORRECT_L,
            "M (Medium)": qrcode.constants.ERROR_CORRECT_M,
            "Q (Quartile)": qrcode.constants.ERROR_CORRECT_Q,
            "H (High)": qrcode.constants.ERROR_CORRECT_H,
        }
        size_map = {"Small": 4, "Medium": 6, "Large": 10}
        return {
            "error_correction": err_map[self.err_combo.get()],
            "box_size": size_map[self.size_combo.get()],
        }

    def generate(self):
        data = self.entry.get().strip()
        if not data:
            messagebox.showwarning("Input required", "Please enter a URL or text.")
            return

        self.set_status("Generating QR code...", "")

        try:
            params = self.get_qr_params()
            qr = qrcode.QRCode(
                version=None,
                error_correction=params["error_correction"],
                box_size=params["box_size"],
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            canvas_size = 260
            display_size = min(canvas_size, img.size[0])
            img_resized = img.resize((display_size, display_size), Image.NEAREST)
            self.qr_image = img
            self.qr_photo = ImageTk.PhotoImage(img_resized)

            self.canvas.delete("all")
            x_off = (canvas_size - display_size) // 2
            self.canvas.create_image(x_off, 0, image=self.qr_photo, anchor="nw")

            save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "QR_Codes")
            os.makedirs(save_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            safe_data = "".join(c for c in data.split("//")[-1].split("/")[0] if c.isalnum() or c in ".-")[:20]
            safe_data = safe_data or "QR"
            filename = f"{safe_data}_{ts}.png"
            file_path = os.path.join(save_dir, filename)
            img.save(file_path)
            self.last_saved_path = file_path

            self.path_label.config(text=f"Saved: {file_path}", fg=self.colors["warning_text"])
            self.path_card.config(highlightbackground=self.colors["success"])

            self.save_btn.config(state="normal")
            self.copy_btn.config(state="normal")
            self.open_btn.config(state="normal")

            self.set_status("QR code generated and saved successfully", self.colors["success"])
        except Exception as e:
            self.set_status(f"Error: {e}", "#DC2626")
            messagebox.showerror("Error", str(e))

    def save_as(self):
        if self.qr_image is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="Save QR Code As"
        )
        if file_path:
            self.qr_image.save(file_path)
            self.last_saved_path = file_path
            self.path_label.config(text=f"Saved: {file_path}", fg=self.colors["warning_text"])
            self.set_status(f"QR code saved to {file_path}", self.colors["success"])

    def copy_path(self):
        if self.last_saved_path:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_saved_path)
            self.set_status("Path copied to clipboard!", self.colors["success"])

    def open_folder(self):
        if self.last_saved_path:
            folder = os.path.dirname(self.last_saved_path)
            os.startfile(folder)

    def set_status(self, text, color):
        self.status_text.config(text=text, fg=color or self.colors["text_secondary"])

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGenerator(root)
    root.mainloop()
