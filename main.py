import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import csv
import time
from deepface import DeepFace
import matplotlib.pyplot as plt

video_capture = cv2.VideoCapture(0)

csv_file_path = "entry_data.csv"
with open(csv_file_path, mode='a', newline='') as csv_file:
    fieldnames = ["ID", "Parent_Name", "Student_Name", "Class_Section", "Entry_Time"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if csv_file.tell() == 0:
        writer.writeheader()

root = tk.Tk()
root.title("Entry Details")
root.geometry("800x600")


entry_counter = 0  

def capture_entry():
    global entry_counter  
    parent_name = parent_name_var.get()
    student_name = student_name_var.get()
    class_section = class_section_var.get()

    if not parent_name or not student_name or not class_section:
        messagebox.showerror("Error", "Please fill in all details.")
        return

    _, frame = video_capture.read()
    

    
    entry_time = time.strftime("%Y-%m-%d %H:%M:%S")

    saved_entry_path = f"entry_frame-{entry_counter}.jpg"
    cv2.imwrite(saved_entry_path, frame)

    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow(
            {
                "ID": entry_counter + 1,
                "Parent_Name": parent_name,
                "Student_Name": student_name,
                "Class_Section": class_section,
                "Entry_Time": entry_time,
            }
        )
    entry_counter += 1
    messagebox.showinfo(
        "Entry Saved", f"Entry details saved for {saved_entry_path}"
    )

    # Clear input fields
    parent_name_var.set('')
    student_name_var.set('')
    class_section_var.set('')


def display_details(entry_id):
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if int(row['ID']) == entry_id:
                # Construct details string
                details = f"Entry ID: {row['ID']}\nParent's Name: {row['Parent_Name']}\nStudent's Name: {row['Student_Name']}\nClass Section: {row['Class_Section']}\nEntry Time: {row['Entry_Time']}"

                # Display details in the tkinter GUI
                label_parent_name.config(text=details)
                break

def recognize_face():
    global entry_counter, exit_counter  # Use the same counter as in capture_entry
    _, frame = video_capture.read()
    
    match_found = False
    matching_entry_id = None
    
    # Perform face recognition for entry frames and exit frames
    for entry_id in range(1, entry_counter + 1):
        entry_frame_path = f"entry_frame-{entry_id}.jpg"
        try:
            result = DeepFace.verify(entry_frame_path, frame)
            if result["verified"]:
                messagebox.showinfo("Face Recognized", f"Face recognized! Details will be shown for entry_frame-{entry_id}.jpg")
                display_details(entry_id)
                return
        except:
            # Handle any exceptions that may occur during face verification
            pass
    
        # Save the face image with the name "exit_frame-{exit_counter}.jpg"
        exit_frame_path = f"exit_frame-{exit_counter}.jpg"
        cv2.imwrite(exit_frame_path, frame)

        try:
            result = DeepFace.verify(entry_frame_path, exit_frame_path)
            if result["verified"]:
                match_found = True
                matching_entry_id = entry_id
                break
        except:
            # Handle any exceptions that may occur during face verification
            pass

    if match_found:
        # Display details for the matching entry frame
        display_details(matching_entry_id)
    else:
        messagebox.showwarning("Unknown Face", "Face not recognized.")

    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

    root.after(10, recognize_face)

    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

    root.after(10, recognize_face)


style = ttk.Style()
style.configure("TButton", padding=(5, 5, 5, 5), font="TkDefaultFont")
style.configure("TLabel", padding=(5, 5, 5, 5), font="TkDefaultFont")
style.configure("TEntry", padding=(5, 5, 5, 5), font="TkDefaultFont")

frame_left = ttk.Frame(root, padding=10)
frame_left.pack(side=tk.LEFT, fill=tk.Y)

frame_right = ttk.Frame(root, padding=10)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

parent_name_var = tk.StringVar()
student_name_var = tk.StringVar()
class_section_var = tk.StringVar()

label_parent_name = ttk.Label(frame_left, text="Parent's Name:")
label_parent_name.grid(row=0, column=0, sticky='w')
entry_parent_name = ttk.Entry(frame_left, textvariable=parent_name_var, width=30)
entry_parent_name.grid(row=0, column=1, pady=5)

label_student_name = ttk.Label(frame_left, text="Student's Name:")
label_student_name.grid(row=1, column=0, sticky='w')
entry_student_name = ttk.Entry(frame_left, textvariable=student_name_var, width=30)
entry_student_name.grid(row=1, column=1, pady=5)

label_class_section = ttk.Label(frame_left, text="Class Section:")
label_class_section.grid(row=2, column=0, sticky='w')
entry_class_section = ttk.Entry(frame_left, textvariable=class_section_var, width=30)
entry_class_section.grid(row=2, column=1, pady=5)

entry_button = ttk.Button(frame_left, text="Capture Entry", command=capture_entry)
entry_button.grid(row=3, column=0, columnspan=2, pady=10)

recognize_button = ttk.Button(frame_left, text="Recognize Face", command=recognize_face)
recognize_button.grid(row=4, column=0, columnspan=2, pady=10)

canvas = tk.Canvas(frame_right, width=640, height=480)
canvas.pack(expand=True, fill=tk.BOTH)

def update():
    _, frame = video_capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

    root.after(10, update)

update()

root.mainloop()

video_capture.release()
cv2.destroyAllWindows()
