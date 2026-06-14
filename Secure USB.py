from tkhtmlview import HTMLLabel
import cv2
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
from tkinter import messagebox
import os
from datetime import datetime
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
import winsound
import time
import webbrowser
import os


def open_project_info():

    path = os.path.abspath("project_information.html")

    webbrowser.open_new_tab(path)



from tkhtmlview import HTMLScrolledText

# ===== CONFIG =====
LOG_FILE = "usb_log.txt"
LOG_DIR = "logs"
INTRUDER_DIR = "intruders"

USERS_FILE = "users.txt"
PASSWORD_EXPIRY = 60  
ALLOWED_EMAILS = [
    "mails",
    "mails"
]   

EMAIL_SENDER = "your email"
EMAIL_PASSWORD ='passkey"


os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(INTRUDER_DIR, exist_ok=True)


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_user(email):
    with open(USERS_FILE, "a") as f:
        f.write(email + "\n")

############ EMAIL VALIDATION ########
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def registration_panel():

    win = tk.Toplevel(root)
    win.geometry("450x340")

    canvas_pw = tk.Canvas(win, width=450, height=340)
    canvas_pw.pack(fill="both", expand=True)

    bg = blur_bg(450, 340)
    if bg:
        canvas_pw.create_image(0, 0, image=bg, anchor="nw")
        canvas_pw.image = bg

    frame = tk.Frame(win, bg="black")
    canvas_pw.create_window(225, 170, window=frame)

    tk.Label(frame, text="Registration", fg="cyan", bg="black",
             font=("Arial", 16)).pack(pady=10)

    tk.Label(frame, text="Enter Email", fg="white", bg="black").pack()
    email_entry = tk.Entry(frame)
    email_entry.pack(pady=5)

    tk.Label(frame, text="Enter OTP", fg="white", bg="black").pack()
    otp_entry = tk.Entry(frame)
    otp_entry.pack(pady=5)

    status = tk.Label(frame, fg="lime", bg="black")
    status.pack()

    otp_data = {"otp": None}

    def send_otp_btn():

        user_email = email_entry.get().strip()

        if not is_valid_email(user_email):
            messagebox.showerror("Error", "Invalid email")
            return

        otp = str(random.randint(100000, 999999))
        otp_data["otp"] = otp

        # OTP sent to owner email
        if send_otp(EMAIL_SENDER, otp):
            status.config(text="OTP sent to Owner Email")

    def register():

        user_email = email_entry.get().strip()
        entered_otp = otp_entry.get().strip()

        if entered_otp != otp_data["otp"]:
            messagebox.showerror("Error", "Invalid OTP")
            return

        users = load_users()

        if user_email in users:
            messagebox.showinfo("Info", "Already registered")
            return

        save_user(user_email)
        write_log(f"REGISTERED: {user_email}")

        messagebox.showinfo("Success", "User Registered Successfully")
        win.destroy()

    tk.Button(frame, text="Send OTP",
              bg="#007BFF", fg="white",
              width=18, command=send_otp_btn).pack(pady=5)

    tk.Button(frame, text="Register",
              bg="#28A745", fg="white",
              width=18, command=register).pack(pady=10)

# ######### SOUND ########
def play_alert_sound():
    winsound.Beep(1000, 400)
    winsound.Beep(800, 400)
    winsound.Beep(1200, 600)

# ===== LOG =====
if os.path.exists(LOG_FILE):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.rename(LOG_FILE, os.path.join(LOG_DIR, f"log_{ts}.txt"))

open(LOG_FILE, "w").write(f"=== Session Started {datetime.now()} ===\n\n")

def write_log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

def view_logs():
    win = tk.Toplevel(root)
    text = tk.Text(win, bg="black", fg="lime")
    text.pack(fill="both", expand=True)
    if os.path.exists(LOG_FILE):
        text.insert("1.0", open(LOG_FILE).read())

# ===== EMAIL SEND =====
def send_email_password(to_email, pwd):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = MIMEText(f"Your temporary password is: {pwd}")
        msg["Subject"] = "USB Security Password"
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email

        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        print("EMAIL ERROR:", e)   # 🔥 shows real error in console
        messagebox.showerror("Error", "Email send failed")
        return False
    
def send_otp(email, otp):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        msg = MIMEText(f"Your OTP for USB Security registration is: {otp}")
        msg["Subject"] = "USB Security OTP"
        msg["From"] = EMAIL_SENDER
        msg["To"] = email

        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("OTP ERROR:", e)
        messagebox.showerror("Error", "OTP send failed")
        return False

# ===== INTRUDER =====
def capture_intruder():
    cam = cv2.VideoCapture(0)
    time.sleep(1)
    ret, frame = cam.read()
    if ret:
        path = os.path.join(INTRUDER_DIR, f"intruder_{datetime.now().strftime('%H%M%S')}.jpg")
        cv2.imwrite(path, frame)
        cam.release()
        return path
    cam.release()
    return None

def send_alert_email(image_path):
    msg = MIMEMultipart()
    msg["Subject"] = "⚠️ Intruder Alert"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_SENDER

    msg.attach(MIMEText("Unauthorized access attempt detected"))

    if image_path:
        with open(image_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename={os.path.basename(image_path)}")
            msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except:
        pass

# ===== MAIN WINDOW =====
root = tk.Tk()
root.title("USB Security")
root.state("zoomed")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

canvas = tk.Canvas(root, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ===== VIDEO =====
cap = cv2.VideoCapture("secure.mp4")
video_bg = None

def update_video():
    global video_bg
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        root.after(30, update_video)
        return

    frame = cv2.resize(frame, (screen_width, screen_height))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))

    if video_bg is None:
        video_bg = canvas.create_image(0, 0, image=img, anchor="nw")
    else:
        canvas.itemconfig(video_bg, image=img)

    canvas.image = img
    root.after(30, update_video)

root.after(100, update_video)

# ===== BLUR =====
def blur_bg(w, h):
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (w, h))
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.filter(ImageFilter.GaussianBlur(10))
        return ImageTk.PhotoImage(img)
    return None

# ===== PASSWORD WINDOW (UPDATED) =====
def password_window(action):
    win = tk.Toplevel(root)
    win.geometry("450x320")

    canvas_pw = tk.Canvas(win, width=450, height=320)
    canvas_pw.pack(fill="both", expand=True)

    bg = blur_bg(450, 320)
    if bg:
        canvas_pw.create_image(0, 0, image=bg, anchor="nw")
        canvas_pw.image = bg

    frame = tk.Frame(win, bg="black")
    canvas_pw.create_window(225, 160, window=frame)

    tk.Label(frame, text="Enter Email", fg="cyan", bg="black").pack(pady=5)
    email = tk.Entry(frame)
    email.pack(pady=5)

    tk.Label(frame, text="Enter Password", fg="white", bg="black").pack()
    entry = tk.Entry(frame, show="*")
    entry.pack(pady=5)

    status = tk.Label(frame, fg="lime", bg="black")
    status.pack()

    temp_data = {"pwd": None, "time": None}

    def generate_password():
        user_email = email.get().strip()

        if not is_valid_email(user_email):
            messagebox.showerror("Error", "Invalid email")
            return

        users = load_users()
        if user_email not in users:
            messagebox.showerror("Access Denied", "Not a registered user ❌")
            return

        pwd = str(random.randint(100000, 999999))
        temp_data["pwd"] = pwd
        temp_data["time"] = time.time()

        if send_email_password(user_email, pwd):
            status.config(text="Password sent ✅")
            write_log(f"PASSWORD SENT to {user_email}")

    def submit():
        if entry.get() == "":
            status.config(text="Enter password")
            return

        # ⏱ EXPIRY CHECK
        if time.time() - temp_data["time"] > PASSWORD_EXPIRY:
            status.config(text="Password expired ❌")
            return

        if entry.get() == temp_data["pwd"]:
            write_log(f"{action.upper()} by {email.get()}")

            if action == "enable":
                os.system(
                    'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v Start /t REG_DWORD /d 3 /f'
                )
            else:
                os.system(
                    'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v Start /t REG_DWORD /d 4 /f'
                )

            messagebox.showinfo("Success", f"{action} successful")
            win.destroy()
        else:
            play_alert_sound()
            img = capture_intruder()
            send_alert_email(img)
            status.config(text="Wrong Password ❌")

    tk.Button(frame, text="Generate Password",
              bg="#007BFF", fg="white", width=20,
              command=generate_password).pack(pady=5)

    tk.Button(frame, text="Submit",
              bg="#28A745", fg="white", width=20,
              command=submit).pack(pady=10)

# ===== NEON BUTTON =====
def neon_button(parent, text, color, command):
    frame = tk.Frame(parent, bg="black")

    btn = tk.Label(frame, text=text,
                   fg=color, bg="black",
                   font=("Arial", 14, "bold"),
                   padx=10, pady=5,
                   cursor="hand2")

    btn.pack()

    # click binding
    btn.bind("<Button-1>", lambda e: command())

    # glow animation colors
    glow_colors = [color, "#00FFFF", "#FFFFFF", "#00FFFF"]
    i = 0

    def animate():
        nonlocal i
        btn.config(fg=glow_colors[i % len(glow_colors)])
        i += 1
        frame.after(200, animate)

    animate()

    return frame

# ===== BUTTONS =====
btn_enable = tk.Button(root, text="Enable USB", bg="green",
                       fg="white", width=15,
                       command=lambda: password_window("enable"))

btn_disable = tk.Button(root, text="Disable USB", bg="red",
                        fg="white", width=15,
                        command=lambda: password_window("disable"))

canvas.create_window(screen_width//3, screen_height-150, window=btn_enable)
canvas.create_window(2*screen_width//3, screen_height-150, window=btn_disable)

btn_project = neon_button(root, "Project Info", "orange", open_project_info)

canvas.create_window(screen_width - 120, 180, window=btn_project)
btn_logs = neon_button(root, "Logs", "cyan", view_logs)
btn_admin = neon_button(root, "Register", "yellow", registration_panel)

canvas.create_window(screen_width - 120, 60, window=btn_logs)
canvas.create_window(screen_width - 120, 120, window=btn_admin)


root.mainloop()
