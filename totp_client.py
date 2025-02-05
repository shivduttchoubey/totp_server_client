import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyotp
import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import base64
import secrets
import re
from datetime import datetime
import threading
import time

class TOTPGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure TOTP Generator")
        self.root.geometry("400x500")
        
        self._current_secret = None
        self._current_totp = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input method buttons
        input_frame = ttk.LabelFrame(main_frame, text="Input Method", padding="10")
        input_frame.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.scan_button = ttk.Button(input_frame, text="Scan QR Code", command=self.scan_qr)
        self.scan_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.file_button = ttk.Button(input_frame, text="Select QR Image", command=self.select_file)
        self.file_button.grid(row=0, column=1, padx=5, pady=5)
        
        # TOTP display
        self.totp_frame = ttk.LabelFrame(main_frame, text="Current TOTP", padding="10")
        self.totp_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.totp_label = ttk.Label(self.totp_frame, text="------", font=("Courier", 24))
        self.totp_label.grid(row=0, column=0, pady=5)
        
        self.progress = ttk.Progressbar(self.totp_frame, length=200, mode='determinate')
        self.progress.grid(row=1, column=0, pady=5)
        
        self.time_label = ttk.Label(self.totp_frame, text="Time remaining: --s")
        self.time_label.grid(row=2, column=0, pady=5)
        
        # Security status
        self.status_frame = ttk.LabelFrame(main_frame, text="Security Status", padding="10")
        self.status_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(self.status_frame, text="✓ Waiting for QR code", foreground="gray")
        self.status_label.grid(row=0, column=0, pady=5)

    def select_file(self):
        """Handle QR code image file selection"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                # Read the image
                image = cv2.imread(file_path)
                if image is None:
                    raise ValueError("Cannot read image file")
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Decode QR code
                decoded_objects = decode(gray)
                if not decoded_objects:
                    raise ValueError("No QR code found in image")
                
                # Process the first QR code found
                self.process_qr_data(decoded_objects[0].data.decode('utf-8'))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
    
    def scan_qr(self):
        """Scan QR code using camera"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access camera")
                return
                
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decoded_objects = decode(gray)
                
                for obj in decoded_objects:
                    cap.release()
                    cv2.destroyAllWindows()
                    self.process_qr_data(obj.data.decode('utf-8'))
                    return
                
                cv2.imshow('Scan QR Code (Press q to quit)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning QR code: {str(e)}")
            
    def process_qr_data(self, data):
        """Process the scanned QR data securely"""
        try:
            if not data.startswith('otpauth://totp/'):
                raise ValueError("Invalid OTP URI format")
                
            secret_match = re.search(r'secret=([A-Z2-7]+=*)', data)
            if not secret_match:
                raise ValueError("No valid secret found in QR code")
                
            secret = secret_match.group(1)
            
            try:
                base64.b32decode(secret)
            except Exception:
                raise ValueError("Invalid secret encoding")
                
            self._current_secret = secret
            self._current_totp = pyotp.TOTP(secret)
            
            self.status_label.config(text="✓ Secret secured in memory", foreground="green")
            
            self.start_totp_updates()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing QR code: {str(e)}")
            self.status_label.config(text="✗ Error processing QR code", foreground="red")
            
    def start_totp_updates(self):
        """Start updating TOTP codes"""
        def update_totp():
            while True:
                try:
                    if self._current_totp:
                        totp = self._current_totp.now()
                        remaining = 30 - datetime.now().timestamp() % 30
                        
                        self.totp_label.config(text=totp)
                        self.time_label.config(text=f"Time remaining: {int(remaining)}s")
                        self.progress['value'] = (remaining / 30) * 100
                        
                    time.sleep(0.1)
                except Exception:
                    break
                    
        threading.Thread(target=update_totp, daemon=True).start()

    def __del__(self):
        """Secure cleanup"""
        self._current_secret = None
        self._current_totp = None

if __name__ == "__main__":
    root = tk.Tk()
    app = TOTPGenerator(root)
    root.mainloop()