import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

class MedicalDeviceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Device Selection")

        # Device selection label and combobox
        ttk.Label(root, text="Select Medical Device:").grid(row=0, column=0, padx=10, pady=10)
        
        self.device_options = ["ECG Machine", "BP Machine", "Thermometer", "Pulse Oximeter", "Stethoscope"]
        self.device_var = tk.StringVar()
        
        self.device_combobox = ttk.Combobox(root, textvariable=self.device_var, values=self.device_options, state='readonly')
        self.device_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Data representation type
        ttk.Label(root, text="Select Data Type:").grid(row=1, column=0, padx=10, pady=10)
        
        self.data_type_var = tk.StringVar()
        self.data_type_combobox = ttk.Combobox(root, textvariable=self.data_type_var, 
                                                values=["Text Only", "Graph", "Combination of Both"], state='readonly')
        self.data_type_combobox.grid(row=1, column=1, padx=10, pady=10)
        
        # Graph options (Single Line or Multiline)
        ttk.Label(root, text="Graph Type:").grid(row=2, column=0, padx=10, pady=10)
        
        self.graph_type_var = tk.StringVar()
        self.graph_type_combobox = ttk.Combobox(root, textvariable=self.graph_type_var, 
                                                 values=["Single Line Graph", "Multi-Line Graph"], state='readonly')
        self.graph_type_combobox.grid(row=2, column=1, padx=10, pady=10)

        # Initially disable graph options
        self.data_type_combobox.bind("<<ComboboxSelected>>", self.toggle_graph_options)
        self.graph_type_combobox.config(state='disabled')

        # Submit button
        submit_button = ttk.Button(root, text="Submit", command=self.show_progress)
        submit_button.grid(row=3, columnspan=2, pady=20)

    def toggle_graph_options(self, event):
        if self.data_type_var.get() == "Graph":
            self.graph_type_combobox.config(state='normal')
        else:
            self.graph_type_combobox.set('')
            self.graph_type_combobox.config(state='disabled')

    def show_progress(self):
        selected_device = self.device_var.get()
        selected_data_type = self.data_type_var.get()
        selected_graph_type = self.graph_type_var.get()

        if not selected_device:
            showinfo("Error", "Please select a medical device.")
            return
        if not selected_data_type:
            showinfo("Error", "Please select a data type.")
            return
        if selected_data_type == "Graph" and not selected_graph_type:
            showinfo("Error", "Please select a graph type.")
            return

        # Display progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Model Development")
        ttk.Label(progress_window, text=f"Model development in progress for {selected_device}...").pack(padx=20, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalDeviceApp(root)
    root.mainloop()
