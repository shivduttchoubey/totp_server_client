import pyotp
import time
import os
import qrcode
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, filedialog

class TOTPAuthenticator:
    def __init__(self, master):
        self.master = master
        self.master.title("TOTP Authenticator")
        self.secret = None
        self.totp = None

        # Create UI elements
        self.label = tk.Label(master, text="Time-based One-Time Password!", font=("Arial", 16))
        self.label.pack(pady=10)

        self.secret_entry = tk.Entry(master, width=40)
        self.secret_entry.pack(pady=5)

        self.generate_button = tk.Button(master, text="Generate New Secret", command=self.generate_secret)
        self.generate_button.pack(pady=5)

        self.use_existing_button = tk.Button(master, text="Use Existing Secret", command=self.use_existing_secret)
        self.use_existing_button.pack(pady=5)

        self.scan_qr_button = tk.Button(master, text="Scan QR Code", command=self.scan_qr_code)
        self.scan_qr_button.pack(pady=5)

        self.code_label = tk.Label(master, text="", font=("Arial", 14))
        self.code_label.pack(pady=10)

        self.timer_label = tk.Label(master, text="", font=("Arial", 14))
        self.timer_label.pack(pady=10)

        self.update_code()

    def generate_secret(self):
        self.secret = pyotp.random_base32()
        messagebox.showinfo("New Secret", f"Your new secret key is: {self.secret}\nSave this secret key securely!")
        self.secret_entry.delete(0, tk.END)
        self.secret_entry.insert(0, self.secret)
        self.totp = pyotp.TOTP(self.secret)

        # Optionally generate a QR code
        account_name = self.secret_entry.get()
        issuer_name = "MyApp"
        self.generate_qr_code(self.secret, account_name, issuer_name)

    def use_existing_secret(self):
        self.secret = self.secret_entry.get().strip()
        if self.secret:
            self.totp = pyotp.TOTP(self.secret)
            messagebox.showinfo("Secret Loaded", "Existing secret key loaded successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid secret key.")

    def scan_qr_code(self):
        image_path = filedialog.askopenfilename(title="Select QR Code Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if image_path:
            secret = self.scan_qr_code_image(image_path)
            if secret:
                self.secret = secret
                self.secret_entry.delete(0, tk.END)
                self.secret_entry.insert(0, self.secret)
                self.totp = pyotp.TOTP(self.secret)
                #messagebox.showinfo("Secret Extracted", f"Extracted secret from QR code: {self.secret}")
            else:
                messagebox.showerror("Error", "Failed to extract the secret from the QR code.")

    def generate_qr_code(self, secret, account_name, issuer_name):
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=account_name, issuer_name=issuer_name)
        qr = qrcode.make(uri)
        file_path = f"{account_name}_qrcode.png"
        qr.save(file_path)
        messagebox.showinfo("QR Code Generated", f"QR code saved as: {file_path}")

    def scan_qr_code_image(self, image_path):
        try:
            img = cv2.imread(image_path)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(img)
            if data:
                secret = data.split("secret=")[1].split("&")[0]
                return secret
            messagebox.showwarning("No QR Code", "No QR code detected in the image!")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading QR code: {e}")
        return None

    def update_code(self):
        if self.totp:
            current_code = self.totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            self.code_label.config(text=f"Current Code: {current_code}")
            self.timer_label.config(text=f"Expires in: {remaining_time}s")
        self.master.after(1000, self.update_code)  # Update every second

if __name__ == "__main__":
    root = tk.Tk()
    app = TOTPAuthenticator(root)
    root.mainloop()