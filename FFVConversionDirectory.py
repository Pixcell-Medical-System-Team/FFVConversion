import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def convert_compressed_avi(filename_p : Path, preserve_orig : bool = False):
    input_file = filename_p.absolute()
    output_file = filename_p.parent / f"{filename_p.stem}_uncompressed.avi"
    cmd = f"ffmpeg -i {input_file} -c:v rawvideo -pix_fmt rgb24 {output_file} -y"
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        print(f"Failed converting {filename_p}. Aborting.")
        return
    # delete original file
    if not preserve_orig:
        filename_p.unlink()

def convert_uncompressed_nut(filename_p : Path, preserve_orig : bool = False):
    input_file = filename_p.absolute()
    output_file = filename_p.parent / f"{filename_p.stem}_ffv1.avi"
    cmd = f"ffmpeg -i {input_file} -c:v ffv1 -pix_fmt bgra {output_file} -y"
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        print(f"{filename_p}: Failed step .nut to .avi (ffv1). Aborting.")
        return
    intermediate_input_file = output_file
    output_file = filename_p.parent / f"{filename_p.stem}_uncompressed.avi"
    cmd = f"ffmpeg -i {intermediate_input_file} -c:v rawvideo -pix_fmt rgb24 {output_file} -y"
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        print(f"<{filename_p}>: Failed step .avi (ffv1) to .avi (uncompressed). Aborting.")
        return
    # delete original and intermediate files
    if not preserve_orig:
        filename_p.unlink()
        intermediate_input_file.unlink()

# Function to process .avi files in the chosen directory and its subdirectories
def process_files(directory):
    # Loop through all subdirectories
    rel_files = [
        p for p in Path(directory).rglob('*')
        if p.suffix.lower() in ('.avi', '.nut')
        and '_uncompressed' not in p.stem.lower()
    ]

    if rel_files:
        for mov in rel_files:
            input_file = mov
            # output_file = os.path.join(root_dir, mov[:-4] + "_uncompressed.avi")
            
            # Attempt to convert the file
            try:
                if input_file.suffix == ".avi":
                    convert_compressed_avi(input_file)
                    status_text.set(f"Converted: {mov}")
                    root.update_idletasks()  # Update the GUI
                else:
                    convert_uncompressed_nut(input_file)
                    status_text.set(f"Converted: {mov}")
                    root.update_idletasks()  # Update the GUI
            except subprocess.CalledProcessError as e:
                status_text.set(f"Error converting {mov}: {e}")
                root.update_idletasks()
                continue

        # # Delete original files after conversion
        # for mov in rel_files:
        #     input_file = os.path.join(root_dir, mov)
        #     try:
        #         os.remove(input_file)
        #         status_text.set(f"Deleted: {mov}")
        #         root.update_idletasks()
        #     except OSError as e:
        #         status_text.set(f"Error deleting {mov}: {e}")
        #         root.update_idletasks()

# GUI setup
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory)
        process_files(directory)

# Main GUI window
root = tk.Tk()
root.title("OC Movie Conversion Tool")
root.geometry("400x200")

# GUI elements
tk.Label(root, text="Select Directory:").pack(pady=5)

dir_entry = tk.Entry(root, width=50)
dir_entry.pack(pady=5)

tk.Button(root, text="Browse", command=select_directory).pack(pady=5)

status_text = tk.StringVar()
status_text.set("Status: Waiting for directory selection")
status_label = tk.Label(root, textvariable=status_text, wraplength=350)
status_label.pack(pady=10)

root.mainloop()
