import cv2
import tkinter as tk
from tkinter import ttk, messagebox, Tk, Label
from PIL import Image, ImageTk
import csv
import time
from deepface import DeepFace
import tkinter.font as tkFont

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
                "ID": entry_counter ,
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

    parent_name_var.set('')
    student_name_var.set('')
    class_section_var.set('')


def display_details(entry_id):
    print(f"Attempting to display details for entry ID: {entry_id}")
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if int(row['ID']) == entry_id:
    
                details = f"Entry ID: {row['ID']}\nParent's Name: {row['Parent_Name']}\nStudent's Name: {row['Student_Name']}\nClass Section: {row['Class_Section']}\nEntry Time: {row['Entry_Time']}"
                print(details)
                label_details.config(text = details,)

                # dialog = tk.Toplevel(root)
                # dialog.title("Entry Details")

                # label_details = ttk.Label(dialog, text=details, padding=(10, 10))
                # label_details.grid(row=0, column=0)

                # ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy)
                # ok_button.grid(row=1, column=0)

                print(f"Details successfully displayed for entry ID: {entry_id}")
                break
        else:
            print(f"No details found for entry ID: {entry_id}")


def recognize_face():
    global entry_counter, exit_counter 

    _, frame = video_capture.read()

    match_found = False
    matching_entry_id = None
 
    exit_frame_path = f"exit_frame-{exit_counter}.jpg"
    cv2.imwrite(exit_frame_path, frame)

    for entry_id in range(1, entry_counter + 1):
        entry_frame_path = f"entry_frame-{entry_id}.jpg"
        try:
       
            result = DeepFace.verify(entry_frame_path, exit_frame_path)
            if result["verified"]:
                match_found = True
                matching_entry_id = entry_id
                break
        except Exception as e:
            print(f"Error verifying exit_frame-{exit_counter} with entry_frame-{entry_id}: {e}")

    if match_found:
        display_details(matching_entry_id)
    else:
        messagebox.showwarning("Unknown Face", "Face not recognized.")
    
    exit_counter += 1


def update():
    _, frame = video_capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

    root.after(10, update)
 

video_capture = cv2.VideoCapture(0)

csv_file_path = "entry_data.csv"
with open(csv_file_path, mode='a', newline='') as csv_file:
    fieldnames = ["ID", "Parent_Name", "Student_Name", "Class_Section", "Entry_Time"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if csv_file.tell() == 0:
        writer.writeheader()

root = Tk()
root.title("Entry Details")
root.geometry("1200x800")

#creating a font object
fontObj = tkFont.Font(size=12)

with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        last_row = None
        for row in reader:
            last_row = row

if last_row:
        last_entry_id = int(last_row['ID'])
        entry_counter = last_entry_id + 1
else:
       entry_counter = 1

exit_counter=0

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

label_details = Label(frame_left, text="Recognized Output:", width=40, height=5, font=fontObj)
label_details.grid(row=5, column=0, sticky='w')

canvas = tk.Canvas(frame_right, width=640, height=480)
canvas.pack(expand=True, fill=tk.BOTH)

update()

root.mainloop()

video_capture.release()
cv2.destroyAllWindows()
  



