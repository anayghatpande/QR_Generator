import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import os
import time
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
            "protected_tag": "#7C3AED",
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

        self.protect_var = tk.BooleanVar(value=False)
        self.protect_chk = tk.Checkbutton(input_card, text="Protect with password",
                                           variable=self.protect_var, font=("Segoe UI", 9),
                                           bg=self.colors["surface"], fg=self.colors["text"],
                                           selectcolor=self.colors["surface"],
                                           activebackground=self.colors["surface"],
                                           activeforeground=self.colors["text"],
                                           cursor="hand2", command=self.toggle_password)
        self.protect_chk.pack(anchor="w", pady=(12, 0))

        self.password_frame = tk.Frame(input_card, bg=self.colors["surface"])
        self.pw_label = tk.Label(self.password_frame, text="Password", font=("Segoe UI", 9),
                                  bg=self.colors["surface"], fg=self.colors["text_secondary"])
        self.pw_label.pack(anchor="w")
        self.pw_entry = tk.Entry(self.password_frame, font=("Segoe UI", 11), show="*",
                                  bg=self.colors["surface"], fg=self.colors["text"],
                                  relief="solid", bd=1, highlightthickness=1,
                                  highlightcolor=self.colors["primary"],
                                  highlightbackground=self.colors["border"])
        self.pw_entry.pack(fill="x", pady=(4, 0), ipady=6, ipadx=8)

        self.pw_confirm_label = tk.Label(self.password_frame, text="Confirm Password",
                                          font=("Segoe UI", 9), bg=self.colors["surface"],
                                          fg=self.colors["text_secondary"])
        self.pw_confirm_label.pack(anchor="w", pady=(8, 0))
        self.pw_confirm = tk.Entry(self.password_frame, font=("Segoe UI", 11), show="*",
                                    bg=self.colors["surface"], fg=self.colors["text"],
                                    relief="solid", bd=1, highlightthickness=1,
                                    highlightcolor=self.colors["primary"],
                                    highlightbackground=self.colors["border"])
        self.pw_confirm.pack(fill="x", pady=(4, 0), ipady=6, ipadx=8)

        self.status_bar = tk.Frame(left, bg=self.colors["bg"])
        self.status_bar.pack(fill="x", pady=(16, 0))

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

        self.protected_badge = tk.Label(preview_card, text="PROTECTED", font=("Segoe UI", 8, "bold"),
                                         bg=self.colors["protected_tag"], fg="white", padx=8, pady=2)

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

        sep = ttk.Separator(preview_card, orient="horizontal")
        sep.pack(fill="x", pady=(14, 0))

        decrypt_row = tk.Frame(preview_card, bg=self.colors["surface"])
        decrypt_row.pack(fill="x", pady=(10, 0))
        tk.Label(decrypt_row, text="Received a protected QR code?",
                 font=("Segoe UI", 9), bg=self.colors["surface"],
                 fg=self.colors["text_secondary"]).pack(side="left")
        self.decrypt_btn = tk.Button(decrypt_row, text="Decrypt QR", font=("Segoe UI", 9, "bold"),
                                      bg=self.colors["surface"], fg=self.colors["protected_tag"],
                                      relief="solid", bd=1, padx=12,
                                      activebackground=self.colors["border"],
                                      cursor="hand2", command=self.open_decrypt_window)
        self.decrypt_btn.pack(side="left", padx=(8, 0), ipady=2)

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
        self.is_protected = False

    def toggle_password(self):
        if self.protect_var.get():
            self.password_frame.pack(fill="x", pady=(8, 0))
        else:
            self.password_frame.pack_forget()

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

    def derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt_url(self, url, password):
        salt = os.urandom(16)
        key = self.derive_key(password, salt)
        f = Fernet(key)
        token = f.encrypt(url.encode())
        combined = base64.urlsafe_b64encode(salt + token).decode()
        return "ENC:" + combined

    def generate(self):
        data = self.entry.get().strip()
        if not data:
            messagebox.showwarning("Input required", "Please enter a URL or text.")
            return

        password = None
        if self.protect_var.get():
            password = self.pw_entry.get()
            confirm = self.pw_confirm.get()
            if not password:
                messagebox.showwarning("Password required", "Enter a password to protect the QR code.")
                return
            if password != confirm:
                messagebox.showwarning("Password mismatch", "Passwords do not match.")
                return

        self.set_status("Generating QR code...")

        try:
            qr_data = data
            if password:
                qr_data = self.encrypt_url(data, password)

            params = self.get_qr_params()
            qr = qrcode.QRCode(
                version=None,
                error_correction=params["error_correction"],
                box_size=params["box_size"],
                border=2,
            )
            qr.add_data(qr_data)
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
            self.is_protected = bool(password)

            if password:
                enc_path = file_path.replace(".png", ".enc")
                with open(enc_path, "w") as f:
                    f.write(qr_data)
                key_path = file_path.replace(".png", ".key")
                with open(key_path, "w") as f:
                    f.write(password)
                path_text = f"Protected QR: {os.path.basename(file_path)}\nEncrypted data: {os.path.basename(enc_path)}"
                self.path_label.config(text=path_text, fg=self.colors["protected_tag"])
                self.protected_badge.pack(anchor="w", pady=(6, 0))
            else:
                self.path_label.config(text=f"Saved: {file_path}", fg=self.colors["warning_text"])
                self.protected_badge.pack_forget()

            self.path_card.config(highlightbackground=self.colors["success"])

            self.save_btn.config(state="normal")
            self.copy_btn.config(state="normal")
            self.open_btn.config(state="normal")

            msg = "Protected QR code generated" if password else "QR code generated and saved"
            self.set_status(msg, self.colors["success"])
        except Exception as e:
            self.set_status(f"Error: {e}")
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

    def set_status(self, text, color=None):
        self.status_text.config(text=text, fg=color or self.colors["text_secondary"])

    def open_decrypt_window(self):
        DecryptWindow(self.root, self.colors)


class DecryptWindow:
    def __init__(self, parent, colors):
        self.win = tk.Toplevel(parent)
        self.win.title("Decrypt Protected QR Code")
        self.win.resizable(False, False)
        self.colors = colors
        self.win.configure(bg=self.colors["bg"])

        main = tk.Frame(self.win, bg=self.colors["bg"], padx=24, pady=24)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="Decrypt QR Code", font=("Segoe UI", 16, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w")
        tk.Label(main, text="Paste the encrypted text or load a .enc file to reveal the original URL",
                 font=("Segoe UI", 10), bg=self.colors["bg"],
                 fg=self.colors["text_secondary"], wraplength=420,
                 justify="left").pack(anchor="w", pady=(4, 16))

        file_frame = tk.Frame(main, bg=self.colors["surface"], padx=16, pady=16,
                               highlightbackground=self.colors["border"],
                               highlightthickness=1)
        file_frame.pack(fill="x")

        tk.Label(file_frame, text="Load .enc file (optional)", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["surface"], fg=self.colors["text"]).pack(anchor="w")

        file_row = tk.Frame(file_frame, bg=self.colors["surface"])
        file_row.pack(fill="x", pady=(8, 0))

        self.file_entry = tk.Entry(file_row, font=("Segoe UI", 10),
                                    bg=self.colors["surface"], fg=self.colors["text"],
                                    relief="solid", bd=1, highlightthickness=1,
                                    highlightcolor=self.colors["primary"],
                                    highlightbackground=self.colors["border"])
        self.file_entry.pack(side="left", fill="x", expand=True, ipady=5, ipadx=8)

        self.browse_btn = tk.Button(file_row, text="Browse", font=("Segoe UI", 10),
                                     bg=self.colors["primary"], fg="white", relief="flat",
                                     padx=16, activebackground=self.colors["primary_hover"],
                                     activeforeground="white", cursor="hand2",
                                     command=self.browse_file)
        self.browse_btn.pack(side="left", padx=(8, 0), ipady=4)

        tk.Label(main, text="OR paste encrypted text manually",
                 font=("Segoe UI", 9), bg=self.colors["bg"],
                 fg=self.colors["text_secondary"]).pack(anchor="w", pady=(12, 6))

        self.enc_text = tk.Text(main, font=("Segoe UI", 10), height=4,
                                 bg=self.colors["surface"], fg=self.colors["text"],
                                 relief="solid", bd=1, highlightthickness=1,
                                 highlightcolor=self.colors["primary"],
                                 highlightbackground=self.colors["border"],
                                 wrap="word")
        self.enc_text.pack(fill="x")

        pw_frame = tk.Frame(main, bg=self.colors["surface"], padx=16, pady=16,
                             highlightbackground=self.colors["border"],
                             highlightthickness=1)
        pw_frame.pack(fill="x", pady=(16, 0))

        tk.Label(pw_frame, text="Password", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["surface"], fg=self.colors["text"]).pack(anchor="w")

        self.pw_entry = tk.Entry(pw_frame, font=("Segoe UI", 11), show="*",
                                  bg=self.colors["surface"], fg=self.colors["text"],
                                  relief="solid", bd=1, highlightthickness=1,
                                  highlightcolor=self.colors["primary"],
                                  highlightbackground=self.colors["border"])
        self.pw_entry.pack(fill="x", pady=(8, 0), ipady=6, ipadx=8)
        self.pw_entry.bind("<Return>", lambda e: self.decrypt())

        self.decrypt_btn = tk.Button(main, text="Decrypt", font=("Segoe UI", 10, "bold"),
                                      bg=self.colors["protected_tag"], fg="white",
                                      relief="flat", padx=24,
                                      activebackground=self.colors["primary_hover"],
                                      activeforeground="white", cursor="hand2",
                                      command=self.decrypt)
        self.decrypt_btn.pack(pady=(16, 0), ipady=6)

        self.result_card = tk.Frame(main, bg=self.colors["surface"], padx=16, pady=16,
                                     highlightbackground=self.colors["border"],
                                     highlightthickness=1)

        self.decrypted_url = None

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Encrypted Data File",
            filetypes=[("Encrypted QR Data", "*.enc"), ("All Files", "*.*")]
        )
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)
            with open(path) as f:
                content = f.read().strip()
            self.enc_text.delete("1.0", tk.END)
            self.enc_text.insert("1.0", content)
            key_path = path.replace(".enc", ".key")
            if os.path.exists(key_path):
                with open(key_path) as f:
                    self.pw_entry.delete(0, tk.END)
                    self.pw_entry.insert(0, f.read().strip())

    def decrypt(self):
        enc_data = self.enc_text.get("1.0", tk.END).strip()
        password = self.pw_entry.get()

        if not enc_data:
            messagebox.showwarning("Data required", "Paste encrypted text or load a .enc file.", parent=self.win)
            return
        if not password:
            messagebox.showwarning("Password required", "Enter the password.", parent=self.win)
            return

        if not enc_data.startswith("ENC:"):
            messagebox.showwarning("Invalid format", "This does not appear to be encrypted QR data (must start with ENC:).", parent=self.win)
            return

        try:
            encrypted_b64 = enc_data[4:]
            raw = base64.urlsafe_b64decode(encrypted_b64)
            salt = raw[:16]
            token = raw[16:]

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            url = f.decrypt(token).decode()

            self.decrypted_url = url
            self.show_result(url)

        except InvalidToken:
            messagebox.showerror("Wrong Password", "Incorrect password. Could not decrypt.", parent=self.win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.win)

    def show_result(self, url):
        for w in self.result_card.winfo_children():
            w.destroy()

        self.result_card.pack(fill="x", pady=(16, 0))

        tk.Label(self.result_card, text="Decrypted URL", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["surface"], fg=self.colors["success"]).pack(anchor="w")

        url_frame = tk.Frame(self.result_card, bg=self.colors["warning_bg"], padx=10, pady=8)
        url_frame.pack(fill="x", pady=(8, 0))

        url_label = tk.Label(url_frame, text=url, font=("Segoe UI", 10),
                              bg=self.colors["warning_bg"], fg=self.colors["text"],
                              wraplength=360, justify="left")
        url_label.pack()

        btn_row = tk.Frame(self.result_card, bg=self.colors["surface"])
        btn_row.pack(fill="x", pady=(10, 0))

        tk.Button(btn_row, text="Open in Browser", font=("Segoe UI", 10, "bold"),
                  bg=self.colors["primary"], fg="white", relief="flat", padx=16,
                  activebackground=self.colors["primary_hover"],
                  activeforeground="white", cursor="hand2",
                  command=lambda: os.startfile(url)).pack(side="left", ipady=4)

        tk.Button(btn_row, text="Copy URL", font=("Segoe UI", 10),
                  bg=self.colors["surface"], fg=self.colors["primary"],
                  relief="solid", bd=1, padx=16,
                  activebackground=self.colors["border"],
                  cursor="hand2",
                  command=lambda: self.copy_url(url)).pack(side="left", padx=(8, 0), ipady=4)

        self.win.geometry("")

    def copy_url(self, url):
        self.win.clipboard_clear()
        self.win.clipboard_append(url)
        messagebox.showinfo("Copied", "URL copied to clipboard.", parent=self.win)


if __name__ == "__main__":
    root = tk.Tk()
    app = QRGenerator(root)
    root.mainloop()
