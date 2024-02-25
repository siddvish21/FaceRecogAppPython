import cv2
import tkinter as tk
from tkinter import ttk, messagebox, Tk, Label
from PIL import Image, ImageTk
import csv
import time
from deepface import DeepFace
import tkinter.font as tkFont
from csv2pdf import convert
import os

current_folder=os.getcwd()
entry_images = os.path.join(current_folder, 'entry_images')
exit_images = os.path.join(current_folder, 'exit_images')

if not os.path.exists(entry_images):
    os.makedirs(entry_images)

if not os.path.exists(exit_images):
    os.makedirs(exit_images)

def clear_details():
    label_details.config(text="")
    
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

    saved_entry_path = os.path.join(entry_images,f"{parent_name}.jpg")
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

    
def show_custom_info(message,title,window_color):
    custom_info_window = tk.Toplevel(root)
    custom_info_window.title(title)
    custom_info_window.geometry("300x100")
    
    custom_font = tkFont.Font(size=14)
    custom_info_window.configure(bg=window_color)
    label = ttk.Label(custom_info_window, text=message, padding=10,font=custom_font)
    label.pack()

    ok_button = ttk.Button(custom_info_window, text="OK", command=custom_info_window.destroy)
    ok_button.pack(pady=10)

def display_details(parent_name):
    print(f"Attempting to display details for entry ID: {parent_name}")
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['Parent_Name'] == parent_name:
                details = f"Entry ID: {row['ID']}\nParent's Name: {row['Parent_Name']}\nStudent's Name: {row['Student_Name']}\nClass Section: {row['Class_Section']}\nEntry Time: {row['Entry_Time']}"
                print(details)
                label_details.config(text=details)
                show_custom_info("FACE DETAILS FOUND!!","SUCCESS!!","#00FF00")
                break
        else:
            print(f"No details found for entry ID: {parent_name}")

def recognize_face():
    global entry_counter, exit_counter, parent_name_var

    _, frame = video_capture.read()
    parent_fields = []
    exit_frame_path = os.path.join(exit_images, "temp_exit_frame.jpg")

    cv2.imwrite(exit_frame_path, frame)

    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            parent_fields.append(row['Parent_Name'])

    for parent_name in parent_fields:
        entry_frame_path = os.path.join(entry_images, f"{parent_name}.jpg")
        try:
            print(f"Verifying {entry_frame_path} with {exit_frame_path}")
            result = DeepFace.verify(entry_frame_path, exit_frame_path, enforce_detection=True)
            if result["verified"]:
                destination_path = os.path.join(exit_images, f"{parent_name}.jpg")

                if os.path.exists(destination_path):
                    print("Exit already done.")
                    show_custom_info("EXIT ALREADY DONE!!!", "EXIT DONE", "#FF0000")
                    break
                else:
                    os.rename(exit_frame_path, destination_path)
                    print("Exit successfully recorded.")
                    display_details(parent_name)
                    break
            else:
                show_custom_info("FACE NOT MATCHED!!", "FAILED", "#FF0000")
                break                                       
        except Exception as e:
            print(f"Error verifying image for {parent_name}: {str(e)}")
            show_custom_info("NO FACE IN FRAME","NO FACE ALERT","#FF0000")
            break
    exit_counter += 1

def generate_report():
    convert("entry_data.csv", "final_report.pdf")
    messagebox.showinfo("Report Generated", "Report successfully generated and saved as 'final_report.pdf'.")

def update():
    _, frame = video_capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

    root.after(10, update)
 

video_capture = cv2.VideoCapture(0)

csv_file_path = "entry_data.csv"


fieldnames = ["ID", "Parent_Name", "Student_Name", "Class_Section", "Entry_Time"]

with open(csv_file_path, mode='a', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if csv_file.tell() == 0:
        writer.writeheader()



root = Tk()
root.title("Entry Details")
root.geometry("1200x800")

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

clear_details_button = ttk.Button(frame_left, text="Clear Details", command=clear_details)
clear_details_button.grid(row=6, column=0, columnspan=2, pady=10)


label_details = Label(frame_left, text="Recognized Output:", width=40, height=5, font=fontObj)
label_details.grid(row=5, column=0, sticky='w')


clear_details_button = ttk.Button(frame_left, text="Clear Details", command=clear_details)
clear_details_button.grid(row=6, column=0, columnspan=2, pady=10)

generate_report_button = ttk.Button(frame_right, text="Generate Report", command=generate_report)
generate_report_button.pack(side=tk.BOTTOM, pady=(0, 25))

canvas = tk.Canvas(frame_right, width=640, height=480)
canvas.pack(expand=True, fill=tk.BOTH)

update()

root.mainloop()

video_capture.release()
cv2.destroyAllWindows()
  



