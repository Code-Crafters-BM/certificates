import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import datetime
import subprocess
import threading
from generator import process_data, generate_single

# App Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CertificateGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Code Crafters Certificate Generator")
        self.geometry("700x650")
        self.configure(fg_color="#0a0a1e")
        
        # State
        self.selected_file = None
        self.selected_template = None
        self.selected_private_key = None
        self.names_list = []
        
        # Build UI
        self.build_ui()
        
    def build_ui(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Code Crafters Certificate Generator", font=ctk.CTkFont(family="Outfit", size=24, weight="bold"), text_color="#f0f3f8")
        title_label.pack(pady=15)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, width=650, height=500, fg_color="#0d1117", segmented_button_selected_color="#007aff", segmented_button_selected_hover_color="#3395ff", segmented_button_unselected_color="#0a0a1e")
        self.tabview.pack(padx=20, pady=5, fill="both", expand=True)
        
        self.tab_gen = self.tabview.add("Generation")
        self.tab_set = self.tabview.add("Advanced Settings")
        
        self.build_generation_tab()
        self.build_settings_tab()

    def build_generation_tab(self):
        # 1. File Upload
        frame_file = ctk.CTkFrame(self.tab_gen, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_file.pack(pady=10, padx=20, fill="x")
        
        self.btn_upload = ctk.CTkButton(frame_file, text="Upload Names File (.txt or .csv)", command=self.upload_file, fg_color="#007aff", hover_color="#3395ff", text_color="white", font=ctk.CTkFont(family="Outfit", weight="bold"))
        self.btn_upload.pack(side="left", padx=10, pady=10)
        
        self.lbl_filename = ctk.CTkLabel(frame_file, text="No file selected", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit"))
        self.lbl_filename.pack(side="left", padx=10)
        
        # 2. Type Selection (Event vs Course)
        frame_type = ctk.CTkFrame(self.tab_gen, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_type.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(frame_type, text="Certificate Type:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left", padx=10, pady=10)
        self.radio_var = ctk.StringVar(value="Course")
        ctk.CTkRadioButton(frame_type, text="Course ('Concept Integration')", variable=self.radio_var, value="Course", fg_color="#007aff", hover_color="#3395ff", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_type, text="Event ('Participation')", variable=self.radio_var, value="Event", fg_color="#007aff", hover_color="#3395ff", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left", padx=10)
        
        # 3. Name & Year
        frame_inputs = ctk.CTkFrame(self.tab_gen, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_inputs.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(frame_inputs, text="Event/Course Name:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_course_name = ctk.CTkEntry(frame_inputs, width=250, placeholder_text="e.g. Python 101", fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit"))
        self.entry_course_name.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(frame_inputs, text="Year:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        current_year = str(datetime.datetime.now().year)
        self.entry_year = ctk.CTkEntry(frame_inputs, width=80, fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit"))
        self.entry_year.insert(0, current_year)
        self.entry_year.grid(row=0, column=3, padx=10, pady=10)
        
        # 4. Template Selector
        frame_template = ctk.CTkFrame(self.tab_gen, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_template.pack(pady=10, padx=20, fill="x")
        
        self.btn_template = ctk.CTkButton(frame_template, text="Select PDF Template", command=self.upload_template, fg_color="#007aff", hover_color="#3395ff", text_color="white", font=ctk.CTkFont(family="Outfit", weight="bold"))
        self.btn_template.pack(side="left", padx=10, pady=10)
        
        self.lbl_template = ctk.CTkLabel(frame_template, text="No template selected", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit"))
        self.lbl_template.pack(side="left", padx=10)

        # 4.5 Private Key Selector
        frame_key = ctk.CTkFrame(self.tab_gen, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_key.pack(pady=10, padx=20, fill="x")
        
        self.btn_key = ctk.CTkButton(frame_key, text="Select Private Key (.pem)", command=self.upload_private_key, fg_color="#007aff", hover_color="#3395ff", text_color="white", font=ctk.CTkFont(family="Outfit", weight="bold"))
        self.btn_key.pack(side="left", padx=10, pady=10)
        
        self.lbl_key = ctk.CTkLabel(frame_key, text="No key selected", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit"))
        self.lbl_key.pack(side="left", padx=10)
        
        # 5. Buttons
        frame_btns = ctk.CTkFrame(self.tab_gen, fg_color="transparent")
        frame_btns.pack(pady=20, padx=20, fill="x")
        
        self.btn_preview = ctk.CTkButton(frame_btns, text="Generate Preview", command=self.generate_preview, fg_color="#007aff", hover_color="#3395ff", text_color="white", font=ctk.CTkFont(family="Outfit", weight="bold"))
        self.btn_preview.pack(side="left", padx=10, expand=True, fill="x")
        
        self.btn_generate = ctk.CTkButton(frame_btns, text="Generate All Certificates", command=self.generate_all, fg_color="#007aff", hover_color="#3395ff", text_color="white", font=ctk.CTkFont(family="Outfit", weight="bold"))
        self.btn_generate.pack(side="left", padx=10, expand=True, fill="x")

        # Status
        self.lbl_status = ctk.CTkLabel(self.tab_gen, text="", text_color="green", font=ctk.CTkFont(family="Outfit"))
        self.lbl_status.pack(pady=5)

    def build_settings_tab(self):
        # Form for tweaking coordinates
        frame_coords = ctk.CTkFrame(self.tab_set, fg_color="#0d1117", corner_radius=10, border_width=1, border_color="#1a1e24")
        frame_coords.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Defaults
        self.settings_vars = {}
        defaults = {
            'name_y': '219.47', 'name_size': '41.46',
            'course_y': '343.37', 'course_size': '30.98',
            'type_y': '450', 'type_size': '16.81',
            'qr_x': '660', 'qr_y': '440', 'qr_size': '110'
        }
        
        rows = [
            ("Name", 'name_y', 'name_size'),
            ("Course", 'course_y', 'course_size'),
            ("Cert Type", 'type_y', 'type_size'),
            ("QR Code", 'qr_x', 'qr_size') # Using qr_size for height/width, we will also add qr_y
        ]
        
        # Headers
        ctk.CTkLabel(frame_coords, text="Element", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit", weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(frame_coords, text="Y Coordinate (from bottom)", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit", weight="bold")).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(frame_coords, text="Font Size / Size", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit", weight="bold")).grid(row=0, column=2, padx=10, pady=10)
        
        # Name
        ctk.CTkLabel(frame_coords, text="Name:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.settings_vars['name_y'] = ctk.StringVar(value=defaults['name_y'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['name_y'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=1, column=1, padx=10)
        self.settings_vars['name_size'] = ctk.StringVar(value=defaults['name_size'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['name_size'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=1, column=2, padx=10)
        
        # Course
        ctk.CTkLabel(frame_coords, text="Course/Event:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.settings_vars['course_y'] = ctk.StringVar(value=defaults['course_y'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['course_y'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=2, column=1, padx=10)
        self.settings_vars['course_size'] = ctk.StringVar(value=defaults['course_size'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['course_size'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=2, column=2, padx=10)
        
        # Cert Type
        ctk.CTkLabel(frame_coords, text="Cert Type:", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.settings_vars['type_y'] = ctk.StringVar(value=defaults['type_y'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['type_y'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=3, column=1, padx=10)
        self.settings_vars['type_size'] = ctk.StringVar(value=defaults['type_size'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['type_size'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=3, column=2, padx=10)
        
        # QR Code
        ctk.CTkLabel(frame_coords, text="QR Code (X, Y):", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=4, column=0, padx=10, pady=10, sticky="e")
        frame_qr_xy = ctk.CTkFrame(frame_coords, fg_color="transparent")
        frame_qr_xy.grid(row=4, column=1, padx=10)
        self.settings_vars['qr_x'] = ctk.StringVar(value=defaults['qr_x'])
        ctk.CTkEntry(frame_qr_xy, textvariable=self.settings_vars['qr_x'], width=60, fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left")
        ctk.CTkLabel(frame_qr_xy, text=" , ", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left")
        self.settings_vars['qr_y'] = ctk.StringVar(value=defaults['qr_y'])
        ctk.CTkEntry(frame_qr_xy, textvariable=self.settings_vars['qr_y'], width=60, fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).pack(side="left")
        
        self.settings_vars['qr_size'] = ctk.StringVar(value=defaults['qr_size'])
        ctk.CTkEntry(frame_coords, textvariable=self.settings_vars['qr_size'], fg_color="#0a0a1e", border_color="#30363d", text_color="#f0f3f8", font=ctk.CTkFont(family="Outfit")).grid(row=4, column=2, padx=10)
        
        ctk.CTkLabel(self.tab_set, text="Note: All coordinates are in points (pt) from the BOTTOM-LEFT of the page.", text_color="gray").pack(pady=10)

    def upload_template(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if not filepath:
            return
        self.selected_template = filepath
        self.lbl_template.configure(text=os.path.basename(filepath))

    def upload_private_key(self):
        filepath = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")])
        if not filepath:
            return
        self.selected_private_key = filepath
        self.lbl_key.configure(text=os.path.basename(filepath))

    def upload_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text/CSV Files", "*.txt *.csv"), ("All Files", "*.*")])
        if not filepath:
            return
            
        self.selected_file = filepath
        self.lbl_filename.configure(text=os.path.basename(filepath))
        
        # Parse names
        self.names_list = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    name = line.strip()
                    if name and not name.startswith('Name,'): # skip csv header if any
                        # Basic csv split fallback if someone uploaded the old format
                        if ',' in name:
                            name = name.split(',')[0].strip()
                        self.names_list.append(name)
            self.lbl_status.configure(text=f"Loaded {len(self.names_list)} names.", text_color="white")
        except Exception as e:
            messagebox.showerror("Error reading file", str(e))

    def get_current_settings(self):
        settings = {}
        for k, var in self.settings_vars.items():
            try:
                settings[k] = float(var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", f"Invalid number for {k}")
                return None
        return settings

    def get_cert_type(self):
        if self.radio_var.get() == "Course":
            return "of Concept Integration"
        return "of Participation"

    def validate_inputs(self):
        if not self.names_list:
            messagebox.showerror("Error", "Please upload a file with names.")
            return False
        if not self.entry_course_name.get().strip():
            messagebox.showerror("Error", "Please enter a Course or Event name.")
            return False
        if not hasattr(self, 'selected_template') or not self.selected_template:
            messagebox.showerror("Error", "Please select a PDF template.")
            return False
        if not hasattr(self, 'selected_private_key') or not self.selected_private_key:
            messagebox.showerror("Error", "Please select your ECC private key (.pem).")
            return False
        return True

    def generate_preview(self):
        if not self.validate_inputs(): return
        settings = self.get_current_settings()
        if not settings: return
        
        course = self.entry_course_name.get().strip()
        year = self.entry_year.get().strip()
        cert_type = self.get_cert_type()
        template = self.selected_template
        name = self.names_list[0]
        
        self.lbl_status.configure(text=f"Generating preview for {name}...", text_color="white")
        
        def run_preview():
            try:
                res = generate_single(
                    name=name, course=course, year=year, cert_type=cert_type, 
                    template_path=template, settings=settings, 
                    base_url="https://code-crafters-bm.github.io/certificates", 
                    serial_counter=0, output_dir="output", private_key_path=self.selected_private_key, is_preview=True
                )
                self.lbl_status.configure(text="Preview generated successfully!", text_color="green")
                # Open PDF
                pdf_path = res['PDF_Path']
                if os.name == 'nt':
                    os.startfile(pdf_path)
                elif os.name == 'posix':
                    subprocess.call(['open', pdf_path])
            except Exception as e:
                self.lbl_status.configure(text=f"Error: {e}", text_color="red")
                
        threading.Thread(target=run_preview).start()

    def generate_all(self):
        if not self.validate_inputs(): return
        settings = self.get_current_settings()
        if not settings: return
        
        course = self.entry_course_name.get().strip()
        year = self.entry_year.get().strip()
        cert_type = self.get_cert_type()
        template = self.selected_template
        
        self.btn_generate.configure(state="disabled")
        self.btn_preview.configure(state="disabled")
        self.lbl_status.configure(text=f"Generating {len(self.names_list)} certificates...", text_color="white")
        
        def run_all():
            try:
                count, _ = process_data(
                    names=self.names_list, course=course, year=year, 
                    cert_type=cert_type, template_path=template, 
                    settings=settings, private_key_path=self.selected_private_key,
                    base_url="https://code-crafters-bm.github.io/certificates", 
                    output_dir="output"
                )
                self.lbl_status.configure(text=f"Success! {count} certificates saved to 'output' folder.", text_color="green")
            except Exception as e:
                self.lbl_status.configure(text=f"Error: {e}", text_color="red")
            finally:
                self.btn_generate.configure(state="normal")
                self.btn_preview.configure(state="normal")
                
        threading.Thread(target=run_all).start()

if __name__ == "__main__":
    app = CertificateGUI()
    app.mainloop()
