"""
GUI Interface for AI Surveillance System
Provides monitoring dashboard and control panel
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import threading
from datetime import datetime
import os
from database import SurveillanceDB
from face_detector import FaceDetector
import config

class SurveillanceGUI:
    def __init__(self):
        """Initialize GUI"""
        self.root = tk.Tk()
        self.root.title("AI Surveillance System - Control Panel")
        self.root.geometry("1400x900")
        
        # Initialize components
        self.db = SurveillanceDB()
        self.face_detector = FaceDetector()
        
        # GUI variables
        self.is_monitoring = False
        self.cap = None
        self.current_frame = None
        
        # Create GUI layout
        self.create_widgets()
        self.update_statistics()
        self.load_recent_detections()
        
        # Start periodic updates
        self.schedule_updates()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === Left Panel - Video Feed ===
        video_frame = ttk.LabelFrame(main_frame, text="Live Feed", padding="10")
        video_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.video_label = ttk.Label(video_frame, text="Camera Inactive", 
                                     background="black", foreground="white")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="Start Monitoring", 
                                    command=self.toggle_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.record_btn = ttk.Button(control_frame, text="Start Recording", 
                                     command=self.toggle_recording, state=tk.DISABLED)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.snapshot_btn = ttk.Button(control_frame, text="Take Snapshot", 
                                       command=self.take_snapshot, state=tk.DISABLED)
        self.snapshot_btn.pack(side=tk.LEFT, padx=5)
        
        # === Top Right - Statistics ===
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        
        # Statistics labels
        self.stats_labels = {}
        stats_data = [
            ("Total Detections:", "total_detections"),
            ("Known Persons:", "known_persons"),
            ("Detections Today:", "detections_today"),
            ("Pending Alerts:", "pending_alerts")
        ]
        
        for i, (label_text, key) in enumerate(stats_data):
            ttk.Label(stats_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
            self.stats_labels[key].grid(row=i, column=1, sticky=tk.E, pady=2, padx=(10, 0))
        
        # === Middle Right - Recent Detections ===
        detections_frame = ttk.LabelFrame(main_frame, text="Recent Detections", padding="10")
        detections_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Treeview for detections
        columns = ("Time", "Person", "Confidence")
        self.detections_tree = ttk.Treeview(detections_frame, columns=columns, 
                                           show="headings", height=10)
        
        for col in columns:
            self.detections_tree.heading(col, text=col)
            self.detections_tree.column(col, width=100)
        
        self.detections_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(detections_frame, orient=tk.VERTICAL, 
                                 command=self.detections_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detections_tree.configure(yscrollcommand=scrollbar.set)
        
        # === Bottom Right - Known Faces Management ===
        known_faces_frame = ttk.LabelFrame(main_frame, text="Known Faces Management", padding="10")
        known_faces_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Listbox for known faces
        list_frame = ttk.Frame(known_faces_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.known_faces_listbox = tk.Listbox(list_frame, height=8)
        self.known_faces_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                      command=self.known_faces_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.known_faces_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(known_faces_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Add Known Face", 
                  command=self.add_known_face).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self.remove_known_face).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh List", 
                  command=self.load_known_faces).pack(side=tk.LEFT, padx=5)
        
        # Load known faces
        self.load_known_faces()
    
    def toggle_monitoring(self):
        """Start/stop camera monitoring"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start camera monitoring"""
        try:
            self.cap = cv2.VideoCapture(config.CAMERA_ID)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Failed to open camera!")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            
            self.is_monitoring = True
            self.start_btn.config(text="Stop Monitoring")
            self.record_btn.config(state=tk.NORMAL)
            self.snapshot_btn.config(state=tk.NORMAL)
            
            self.db.log_system_event("INFO", "Monitoring started from GUI")
            
            # Start video feed thread
            threading.Thread(target=self.update_video_feed, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop camera monitoring"""
        self.is_monitoring = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.video_label.config(image="", text="Camera Inactive")
        self.start_btn.config(text="Start Monitoring")
        self.record_btn.config(state=tk.DISABLED)
        self.snapshot_btn.config(state=tk.DISABLED)
        
        self.db.log_system_event("INFO", "Monitoring stopped from GUI")
    
    def update_video_feed(self):
        """Update video feed in real-time"""
        frame_count = 0
        
        while self.is_monitoring and self.cap:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Detect faces periodically
            if frame_count % config.DETECTION_INTERVAL == 0:
                faces = self.face_detector.detect_faces(frame)
                
                for face in faces:
                    # Recognize face
                    embedding = self.face_detector.get_face_embedding(face)
                    person_name, similarity = self.face_detector.recognize_face(embedding)
                    
                    # Draw box
                    frame = self.face_detector.draw_face_box(frame, face, person_name, similarity)
            
            # Convert frame for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (800, 600))
            
            # Convert to ImageTk
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk, text="")
            
            self.current_frame = frame
    
    def toggle_recording(self):
        """Toggle video recording"""
        # This would integrate with the recording system
        messagebox.showinfo("Recording", "Recording feature - integrate with main recording system")
    
    def take_snapshot(self):
        """Take a snapshot from current frame"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            filepath = os.path.join(config.DATA_DIR, filename)
            
            cv2.imwrite(filepath, self.current_frame)
            messagebox.showinfo("Snapshot", f"Snapshot saved: {filename}")
            self.db.log_system_event("INFO", f"Snapshot saved: {filename}")
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.db.get_statistics()
        
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))
    
    def load_recent_detections(self):
        """Load recent detections into treeview"""
        # Clear existing items
        for item in self.detections_tree.get_children():
            self.detections_tree.delete(item)
        
        # Load from database
        detections = self.db.get_recent_detections(limit=20)
        
        for detection in detections:
            # detection = (id, timestamp, person_id, person_name, confidence, ...)
            time_str = datetime.fromisoformat(detection[1]).strftime("%H:%M:%S")
            person = detection[3] if detection[3] else "Unknown"
            confidence = f"{detection[4]:.2f}" if detection[4] else "N/A"
            
            self.detections_tree.insert("", 0, values=(time_str, person, confidence))
    
    def load_known_faces(self):
        """Load known faces into listbox"""
        self.known_faces_listbox.delete(0, tk.END)
        
        for name in self.face_detector.known_faces.keys():
            self.known_faces_listbox.insert(tk.END, name)
    
    def add_known_face(self):
        """Add a new known face"""
        # Open dialog to select image
        filepath = filedialog.askopenfilename(
            title="Select face image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        # Ask for name
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Name")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Enter person's name:").pack(pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def submit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a name")
                return
            
            # Copy image to known_faces directory
            import shutil
            ext = os.path.splitext(filepath)[1]
            dest_path = os.path.join(config.KNOWN_FACES_DIR, f"{name}{ext}")
            shutil.copy(filepath, dest_path)
            
            # Add to face detector
            if self.face_detector.add_known_face(name, dest_path):
                self.db.add_known_person(name, dest_path)
                messagebox.showinfo("Success", f"Added known face: {name}")
                self.load_known_faces()
                self.update_statistics()
            else:
                messagebox.showerror("Error", "Failed to add face. Make sure the image contains a clear face.")
            
            dialog.destroy()
        
        ttk.Button(dialog, text="Submit", command=submit).pack(pady=5)
    
    def remove_known_face(self):
        """Remove selected known face"""
        selection = self.known_faces_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a face to remove")
            return
        
        name = self.known_faces_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm", f"Remove known face: {name}?"):
            if name in self.face_detector.known_faces:
                del self.face_detector.known_faces[name]
                self.face_detector.save_known_faces()
                self.load_known_faces()
                messagebox.showinfo("Success", f"Removed: {name}")
    
    def schedule_updates(self):
        """Schedule periodic updates"""
        self.update_statistics()
        self.load_recent_detections()
        
        # Schedule next update in 5 seconds
        self.root.after(5000, self.schedule_updates)
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_monitoring:
            self.stop_monitoring()
        
        self.db.close()
        self.root.destroy()

def main():
    """Main entry point for GUI"""
    app = SurveillanceGUI()
    app.run()

if __name__ == "__main__":
    main()
