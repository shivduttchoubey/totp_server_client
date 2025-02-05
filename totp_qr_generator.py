import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
import pyotp
import base64
from PIL import Image, ImageTk
import secrets
import os

class TOTPQRGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("TOTP QR Code Generator")
        self.root.geometry("400x600")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input fields
        ttk.Label(main_frame, text="Account Name:").grid(row=0, column=0, pady=5)
        self.account_entry = ttk.Entry(main_frame)
        self.account_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Issuer:").grid(row=1, column=0, pady=5)
        self.issuer_entry = ttk.Entry(main_frame)
        self.issuer_entry.grid(row=1, column=1, pady=5)
        
        # Generate button
        self.generate_button = ttk.Button(main_frame, text="Generate QR Code", command=self.generate_qr)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # QR code display
        self.qr_frame = ttk.LabelFrame(main_frame, text="Generated QR Code", padding="10")
        self.qr_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.qr_label = ttk.Label(self.qr_frame)
        self.qr_label.grid(row=0, column=0, pady=5)
        
        # Secret display
        self.secret_frame = ttk.LabelFrame(main_frame, text="Secret Key", padding="10")
        self.secret_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.secret_label = ttk.Label(self.secret_frame, text="", font=("Courier", 12))
        self.secret_label.grid(row=0, column=0, pady=5)
        
    def generate_qr(self):
        """Generate new TOTP secret and QR code"""
        try:
            # Generate random secret
            secret = pyotp.random_base32()
            
            # Get account details
            account = self.account_entry.get().strip()
            issuer = self.issuer_entry.get().strip()
            
            if not account or not issuer:
                raise ValueError("Please fill in all fields")
            
            # Generate OTP URI
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=account,
                issuer_name=issuer
            )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to PhotoImage for display
            qr_photo = ImageTk.PhotoImage(qr_image)
            self.qr_label.config(image=qr_photo)
            self.qr_label.image = qr_photo  # Keep reference
            
            # Display secret
            self.secret_label.config(text=f"Secret: {secret}")
            
            # Save QR code
            save_path = f"totp_qr_{account}.png"
            qr_image.save(save_path)
            messagebox.showinfo("Success", f"QR code saved as {save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = TOTPQRGenerator(root)
    root.mainloop()