import tkinter as tk
from tkinter import ttk, scrolledtext, PhotoImage, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import sys
import os
import time
from datetime import datetime
from pathlib import Path
import networkmonitor

class BackgroundFrame(ttk.Frame):
    """A frame that supports a background image that scales with the window"""
    def __init__(self, parent, image_path, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        try:
            # Load original image
            self.original_image = Image.open(image_path)
            self.aspect_ratio = self.original_image.width / self.original_image.height
            
            # Create initial photo image
            self.background_image = None
            self.background_label = tk.Label(self)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Bind resize event
            self.bind('<Configure>', self.resize_image)
            
            # Make sure other widgets appear on top
            self.background_label.lower()
            
        except Exception as e:
            print(f"Could not load background image: {e}")
    
    def resize_image(self, event):
        """Resize the background image to maintain aspect ratio and fill the window"""
        if self.original_image:
            # Get new size
            width = event.width
            height = event.height
            
            # Calculate new size maintaining aspect ratio
            new_ratio = width / height
            
            if new_ratio > self.aspect_ratio:
                # Window is wider than image ratio
                new_height = height
                new_width = int(height * self.aspect_ratio)
            else:
                # Window is taller than image ratio
                new_width = width
                new_height = int(width / self.aspect_ratio)
            
            # Resize image
            resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.background_image = ImageTk.PhotoImage(resized_image)
            self.background_label.configure(image=self.background_image)

class MonitorWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("NetConMon - Network Connection Monitor")
        self.window.geometry("800x600")
        
        # Create background frame
        self.main_frame = BackgroundFrame(self.window, "netconmon.png")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status and backup labels frame
        labels_frame = tk.Frame(self.main_frame, bg='black')
        labels_frame.pack(pady=5)
        
        # Protocol selector frame
        self.protocol_frame = tk.Frame(labels_frame, bg='black')
        self.protocol_frame.pack(pady=2)
        
        # TCP Status label
        self.tcp_status_label = tk.Label(
            self.protocol_frame,
            text="TCP Connections: 0",
            font=("Arial", 12),
            fg='white',
            bg='black'
        )
        self.tcp_status_label.pack(side=tk.LEFT, padx=10)
        
        # UDP Status label
        self.udp_status_label = tk.Label(
            self.protocol_frame,
            text="UDP Connections: 0",
            font=("Arial", 12),
            fg='white',
            bg='black'
        )
        self.udp_status_label.pack(side=tk.LEFT, padx=10)
        
        # Total Status label
        self.total_status_label = tk.Label(
            labels_frame,
            text="Total Connections: 0",
            font=("Arial", 12),
            fg='white',
            bg='black'
        )
        self.total_status_label.pack(pady=2)
        
        # Backup status label
        self.backup_label = tk.Label(
            labels_frame,
            text="No backups yet",
            font=("Arial", 10),
            fg='white',
            bg='black'
        )
        self.backup_label.pack(pady=2)
        
        # Log area with protocol filter
        log_frame = tk.Frame(self.main_frame, bg='black')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Protocol filter
        filter_frame = tk.Frame(log_frame, bg='black')
        filter_frame.pack(fill=tk.X, pady=2)
        
        # Protocol filter checkboxes
        self.show_tcp = tk.BooleanVar(value=True)
        self.show_udp = tk.BooleanVar(value=True)
        
        tcp_check = tk.Checkbutton(
            filter_frame,
            text="Show TCP",
            variable=self.show_tcp,
            fg='white',
            bg='black',
            selectcolor='black',
            activebackground='black',
            activeforeground='white'
        )
        tcp_check.pack(side=tk.LEFT, padx=5)
        
        udp_check = tk.Checkbutton(
            filter_frame,
            text="Show UDP",
            variable=self.show_udp,
            fg='white',
            bg='black',
            selectcolor='black',
            activebackground='black',
            activeforeground='white'
        )
        udp_check.pack(side=tk.LEFT, padx=5)
        
        # Log area
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            font=("Arial", 10),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='white'
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Create independent frames for buttons
        start_frame = tk.Frame(self.main_frame, bg='black')
        start_frame.place(relx=0.30, rely=0.9, anchor=tk.CENTER)
        
        stop_frame = tk.Frame(self.main_frame, bg='black')
        stop_frame.place(relx=0.50, rely=0.9, anchor=tk.CENTER)
        
        export_frame = tk.Frame(self.main_frame, bg='black')
        export_frame.place(relx=0.70, rely=0.9, anchor=tk.CENTER)
        
        # Create buttons
        self.start_button = tk.Button(
            start_frame,
            text="Start",
            font=("Arial", 16, "bold"),
            fg='black',
            bg='white',
            width=10,
            height=2,
            relief=tk.RIDGE,
            borderwidth=2,
            command=self.start_monitoring
        )
        self.start_button.pack()
        
        self.stop_button = tk.Button(
            stop_frame,
            text="Stop",
            font=("Arial", 16, "bold"),
            fg='black',
            bg='white',
            width=10,
            height=2,
            relief=tk.RIDGE,
            borderwidth=2,
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_button.pack()
        
        self.export_button = tk.Button(
            export_frame,
            text="Export",
            font=("Arial", 16, "bold"),
            fg='black',
            bg='white',
            width=10,
            height=2,
            relief=tk.RIDGE,
            borderwidth=2,
            command=self.export_results,
            state=tk.DISABLED
        )
        self.export_button.pack()
        
        self.is_monitoring = False
        self.monitor_thread = None
        self.tracker = None
        self.backup_interval = 5  # seconds
        self.last_backup = time.time()
        self.backup_count = 0

    def log_message(self, message, protocol=''):
        """Log a message if its protocol type is enabled in filters"""
        if protocol == 'TCP' and not self.show_tcp.get():
            return
        if protocol == 'UDP' and not self.show_udp.get():
            return
        
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)

    def update_status(self):
        """Update all status labels with current connection counts"""
        if self.tracker:
            self.tcp_status_label.config(
                text=f"TCP Connections: {self.tracker.total_tcp_tracked}"
            )
            self.udp_status_label.config(
                text=f"UDP Connections: {self.tracker.total_udp_tracked}"
            )
            self.total_status_label.config(
                text=f"Total Connections: {self.tracker.total_tracked}"
            )

    def start_monitoring(self):
        self.is_monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log_message("Starting network monitoring...")
        
        self.monitor_thread = threading.Thread(target=self.monitor_connections)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_connections(self):
        self.tracker = networkmonitor.ConnectionTracker()
        while self.is_monitoring:
            try:
                current_connections = networkmonitor.get_current_connections()
                new_connections = self.tracker.update(current_connections)
                
                # Update status for both TCP and UDP connections
                self.window.after(0, self.update_status)
                
                for conn in new_connections:
                    protocol = conn[5]  # Get protocol from connection info
                    remote_info = f"{conn[2]}:{conn[3]}" if conn[2] else "No remote endpoint"
                    message = f"New {protocol} connection: {conn[0]}:{conn[1]} → {remote_info} ({conn[4]})"
                    self.window.after(0, self.log_message, message, protocol)
                
                # Perform auto-backup
                self.auto_backup()
                
                threading.Event().wait(0.1)
            except Exception as e:
                self.window.after(0, self.log_message, f"Error: {str(e)}")
                break

    def auto_backup(self):
        """Perform automatic backup of current data"""
        if self.tracker and self.is_monitoring:
            try:
                current_time = time.time()
                if current_time - self.last_backup >= self.backup_interval:
                    backup_dir = networkmonitor.get_local_backup_directory()
                    
                    # Keep only the latest backup file
                    for old_file in backup_dir.glob('*_current.*'):
                        old_file.unlink()
                    
                    csv_filename = backup_dir / f'network_connections_current.csv'
                    txt_filename = backup_dir / f'network_connections_current.txt'
                    
                    networkmonitor.write_to_csv(self.tracker, csv_filename)
                    networkmonitor.write_to_txt(self.tracker, txt_filename)
                    
                    self.backup_count += 1
                    self.backup_label.config(
                        text=f"Last backup: {datetime.now().strftime('%H:%M:%S')} "
                             f"(Backup count: {self.backup_count})"
                    )
                    self.last_backup = current_time
                    
            except Exception as e:
                self.log_message(f"Backup error: {str(e)}")

    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL)
        self.log_message("\nStopping network monitoring...")
        self.save_final_backup()

    def save_final_backup(self):
        """Save final backup to the backup directory"""
        if self.tracker:
            try:
                backup_dir = networkmonitor.get_local_backup_directory()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                csv_filename = backup_dir / f'network_connections_final_{timestamp}.csv'
                txt_filename = backup_dir / f'network_connections_final_{timestamp}.txt'
                
                networkmonitor.write_to_csv(self.tracker, csv_filename)
                networkmonitor.write_to_txt(self.tracker, txt_filename)
                
                self.log_message(f"\nFinal backup saved to backup folder:")
                self.log_message(f"CSV: {csv_filename.name}")
                self.log_message(f"TXT: {txt_filename.name}")
                
            except Exception as e:
                self.log_message(f"Error saving final backup: {str(e)}")

    def export_results(self):
        """Export results to user-selected directory"""
        if not self.tracker:
            messagebox.showerror("Error", "No monitoring data available to export!")
            return
            
        try:
            export_dir = filedialog.askdirectory(
                title="Select Export Directory",
                initialdir=str(Path.home())
            )
            
            if export_dir:  # User selected a directory
                export_dir = Path(export_dir)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                csv_filename = export_dir / f'network_connections_{timestamp}.csv'
                txt_filename = export_dir / f'network_connections_{timestamp}.txt'
                
                networkmonitor.write_to_csv(self.tracker, csv_filename)
                networkmonitor.write_to_txt(self.tracker, txt_filename)
                
                self.log_message(f"\nResults exported to:")
                self.log_message(f"CSV: {csv_filename}")
                self.log_message(f"TXT: {txt_filename}")
                
                messagebox.showinfo(
                    "Export Complete",
                    f"Files have been exported to:\n{export_dir}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error exporting results:\n{str(e)}"
            )

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("NetConMon")
        
        # Window sizing
        min_width = 960
        min_height = 540
        self.window.minsize(min_width, min_height)
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        if screen_width >= 1920 and screen_height >= 1080:
            self.window.geometry("1920x1080")
        else:
            self.window.geometry(f"{min_width}x{min_height}")
        
        # Background frame
        main_frame = BackgroundFrame(self.window, "netconmon.png")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create independent frames for each button
        run_frame = tk.Frame(main_frame, bg='')
        run_frame.place(relx=0.40, rely=0.5, anchor=tk.CENTER)
        
        doc_frame = tk.Frame(main_frame, bg='')
        doc_frame.place(relx=0.60, rely=0.5, anchor=tk.CENTER)
        
        # Create and style buttons
        self.run_button = tk.Button(
            run_frame,
            text="Run",
            font=("Arial", 16, "bold"),
            fg='black',
            bg='white',
            width=10,
            height=2,
            relief=tk.RIDGE,
            borderwidth=2,
            command=self.run_monitor
        )
        self.run_button.pack()
        
        self.doc_button = tk.Button(
            doc_frame,
            text="Info",
            font=("Arial", 16, "bold"),
            fg='black',
            bg='white',
            width=12,
            height=2,
            relief=tk.RIDGE,
            borderwidth=2,
            command=self.open_documentation
        )
        self.doc_button.pack()

    def run_monitor(self):
        monitor_window = MonitorWindow()
        monitor_window.window.mainloop()

    def open_documentation(self):
        doc_path = Path("readme.txt")
        if doc_path.exists():
            if sys.platform == "win32":
                os.startfile(doc_path)
            else:
                import subprocess
                subprocess.run(["open", doc_path] if sys.platform == "darwin" else ["xdg-open", doc_path])
        else:
            messagebox.showerror("Error", "Documentation file (readme.txt) not found!")

def main():
    if not networkmonitor.check_privileges():
        messagebox.showerror(
            "Error",
            "Please run with administrator privileges:\n\n" +
            "Windows: Right-click, Run as Administrator\n" +
            "Mac/Linux: Use sudo python3 netconmon.py"
        )
        sys.exit(1)
    
    main_window = MainWindow()
    main_window.window.mainloop()

if __name__ == "__main__":
    main()