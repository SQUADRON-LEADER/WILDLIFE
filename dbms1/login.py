import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from PIL import Image, ImageTk
import os
import time
from pathlib import Path
from datetime import datetime

# MySQL connection
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="11223344",  
        database="WildGuardDB"
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
    exit(1)

# Function to center window
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# Show success animation
def show_success_animation(username):
    # Create overlay window
    success_window = tk.Toplevel(root)
    success_window.overrideredirect(True)  # No window decorations
    success_window.attributes("-topmost", True)  # Keep on top
    
    # Size and position
    win_width, win_height = 300, 200
    center_window(success_window, win_width, win_height)
    
    # Dark green background
    success_window.configure(bg="#1e8449")
    
    # Add faster fade-in effect (5 steps instead of 10)
    success_window.attributes('-alpha', 0.0)
    for i in range(5):
        success_window.attributes('-alpha', (i+1)/5)
        success_window.update()
        time.sleep(0.02)  # Faster fade-in (0.02s vs 0.05s)
    
    # Success checkmark and message - same as before
    check_label = tk.Label(
        success_window,
        text="✓",
        font=("Segoe UI", 60),
        fg="white",
        bg="#1e8449"
    )
    check_label.pack(pady=(40, 5))
    
    success_text = tk.Label(
        success_window,
        text=f"Welcome, {username}!",
        font=("Segoe UI", 16, "bold"),
        fg="white",
        bg="#1e8449"
    )
    success_text.pack(pady=5)
    
    # Brief animation before proceeding
    def close_and_proceed():
        # Faster fade out (5 steps instead of 10)
        for i in range(5, -1, -1):
            success_window.attributes('-alpha', i/5)
            success_window.update()
            time.sleep(0.02)  # Faster fade-out (0.02s vs 0.04s)
        success_window.destroy()
        root.destroy()
        import dashboard
        dashboard.Dashboard(username=username).mainloop()
    
    # Reduced animation time (1.2 seconds instead of 2.5)
    root.after(1200, close_and_proceed)

def animate_frame_transition(hide_frame, show_frame):
    """Animate transition between frames with shorter duration"""
    # Configure frames for animation
    hide_frame.configure(bg="#ffffff")
    show_frame.configure(bg="#ffffff")
    
    # Get window width for slide calculation
    width = root.winfo_width()
    
    # Position the show_frame to the right, off-screen
    show_frame.place(x=width, y=0, width=width)
    
    # Faster animation (10 steps instead of 20)
    steps = 10
    for i in range(steps + 1):
        hide_x = -i * (width // steps)
        show_x = width + hide_x
        hide_frame.place(x=hide_x)
        show_frame.place(x=show_x)
        root.update()
        time.sleep(0.015)  # Faster delay (0.015s vs 0.025s)
    
    hide_frame.place_forget()
    show_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Register function
def register_user():
    # Get values from registration entry fields
    user = entry_username_reg.get()
    pwd = entry_password_reg.get()
    confirm_pwd = entry_confirm.get()

    if user == "" or pwd == "" or confirm_pwd == "":
        show_notification("All fields are required", "warning")
        return
    
    if pwd != confirm_pwd:
        show_notification("Passwords do not match", "error")
        return

    if len(pwd) < 6:
        show_notification("Password must be at least 6 characters", "warning")
        return
        
    try:
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (user, pwd))
        conn.commit()
        show_notification("Account created successfully!", "success")
        show_login_frame()
    except mysql.connector.IntegrityError:
        show_notification("Username already exists", "error")

# Login function
def login_user():
    user = entry_username.get()
    pwd = entry_password.get()

    if user == "" or pwd == "":
        show_notification("Username and password required", "warning")
        return

    cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (user, pwd))
    result = cursor.fetchone()

    if result:
        # Close connection before destroying the window
        try:
            conn.close()
        except:
            pass
        
        # Show success animation instead of message box
        show_success_animation(user)
    else:
        show_notification("Invalid username or password", "error")
        
# Show register frame with animation
def show_register_frame():
    animate_frame_transition(login_frame, register_frame)
    register_heading_label.config(text="Create an Account")
    root.title("WildGuard - Register")

# Show login frame with animation
def show_login_frame():
    animate_frame_transition(register_frame, login_frame)
    login_heading_label.config(text="Welcome Back")
    root.title("WildGuard - Login")
    
# Toggle password visibility
def toggle_password(entry, button):
    if entry.cget('show') == '•':
        entry.config(show='')
        button.config(text="🔒")
    else:
        entry.config(show='•')
        button.config(text="👁️")

# Create hover effect
def create_hover_effect(widget, enter_color, leave_color):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_color))

# Show notification
def show_notification(message, message_type="info"):
    # Colors and icons remain the same
    colors = {
        "success": "#27ae60", "info": "#3498db", 
        "warning": "#f39c12", "error": "#e74c3c"
    }
    
    icons = {
        "success": "✓", "info": "ℹ", 
        "warning": "⚠", "error": "✕"
    }
    
    color = colors.get(message_type, "#3498db")
    icon = icons.get(message_type, "ℹ")
    
    # Create notification frame
    notif = tk.Toplevel(root)
    notif.overrideredirect(True)
    notif.attributes('-topmost', True)
    
    # Size and position
    width, height = 300, 60
    x = root.winfo_x() + (root.winfo_width() - width) // 2
    y = root.winfo_y() + 20
    notif.geometry(f"{width}x{height}+{x}+{y}")
    notif.configure(bg=color)
    
    # Content frame
    content = tk.Frame(notif, bg=color, padx=10, pady=10)
    content.pack(fill="both", expand=True)
    
    # Icon and message in a row
    icon_label = tk.Label(content, text=icon, font=("Segoe UI", 16), fg="white", bg=color)
    icon_label.pack(side="left", padx=(5, 10))
    
    msg_label = tk.Label(content, text=message, font=("Segoe UI", 10), 
                        fg="white", bg=color, anchor="w", justify="left")
    msg_label.pack(side="left", fill="both", expand=True)
    
    # Close button
    close_btn = tk.Label(content, text="×", font=("Segoe UI", 16), 
                       fg="white", bg=color, cursor="hand2")
    close_btn.pack(side="right", padx=5)
    close_btn.bind("<Button-1>", lambda e: notif.destroy())
    
    # Faster fade-in (8 steps vs 15)
    notif.attributes('-alpha', 0.0)
    for i in range(8):
        notif.attributes('-alpha', (i+1)/8)
        notif.update()
        time.sleep(0.02)  # Faster fade-in (0.02s vs 0.035s)
    
    # Shorter display time (2.0s vs 3.5s)
    notif.after(2000, lambda: fade_out_and_destroy(notif))

def fade_out_and_destroy(window):
    """Faster fade out effect"""
    # Fewer steps (8 vs 15)
    for i in range(8, -1, -1):
        window.attributes('-alpha', i/8)
        window.update()
        time.sleep(0.02)  # Faster fade-out (0.02s vs 0.035s)
    window.destroy()

# GUI Setup
root = tk.Tk()
root.title("WildGuard - Login")
root.configure(bg="#ffffff")
center_window(root, 900, 600)  # Wider window for split design
root.resizable(True, True)     # Allow resizing

# Define color scheme - wildlife/forest theme
colors = {
    "primary": "#1e8449",      # Dark green
    "secondary": "#27ae60",    # Medium green
    "accent": "#2ecc71",       # Light green
    "text_dark": "#333333",
    "text_light": "#ffffff",
    "text_muted": "#7f8c8d",
    "bg_light": "#ffffff",
    "bg_dark": "#1e8449",
    "warning": "#f39c12",
    "error": "#e74c3c"
}

# Create a style for widgets
style = ttk.Style()
style.theme_use('clam')  # Use clam theme as base

style.configure('TButton', 
                font=('Segoe UI', 10, 'bold'),
                background=colors["secondary"])

style.configure('TEntry', 
                font=('Segoe UI', 10),
                fieldbackground="#f8f9fa")

style.map('TButton', 
          background=[('active', colors["accent"])])

# Create a two-panel design
main_frame = tk.Frame(root, bg="#ffffff")
main_frame.pack(fill="both", expand=True)

# Left panel - Forest green background with wildlife theme
left_panel = tk.Frame(main_frame, bg=colors["bg_dark"], width=400)
left_panel.pack(side="left", fill="both", expand=True)

# Decoration/Logo area at the top of left panel
logo_frame = tk.Frame(left_panel, bg=colors["bg_dark"], height=200)
logo_frame.pack(fill="x", pady=(80, 20))

# Try to load logo
try:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpeg")
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((140, 100), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        
        logo_label = tk.Label(logo_frame, image=logo_photo, bg=colors["bg_dark"])
        logo_label.image = logo_photo
        logo_label.pack(pady=10)
except Exception as e:
    print(f"Error loading logo: {e}")
    # Show text instead
    tk.Label(
        logo_frame, 
        text="🦁", 
        font=("Segoe UI", 60), 
        fg=colors["text_light"], 
        bg=colors["bg_dark"]
    ).pack(pady=(20, 0))

# App title on left panel
tk.Label(
    left_panel, 
    text="WildGuard", 
    font=("Segoe UI", 32, "bold"), 
    fg=colors["text_light"], 
    bg=colors["bg_dark"]
).pack(pady=(10, 5))

tk.Label(
    left_panel,
    text="Wildlife Conservation Management",
    font=("Segoe UI", 14),
    fg=colors["text_light"],
    bg=colors["bg_dark"]
).pack(pady=(0, 30))

# Decorative divider
divider = tk.Frame(left_panel, height=2, bg="#ffffff", width=100)
divider.pack(pady=20)

# Inspirational quote
quote_frame = tk.Frame(left_panel, bg=colors["bg_dark"], padx=40, pady=20)
quote_frame.pack(fill="x")

tk.Label(
    quote_frame,
    text="The greatest threat to our planet is the belief that someone else will save it.",
    font=("Georgia", 12, "italic"),
    fg=colors["text_light"],
    bg=colors["bg_dark"],
    wraplength=300,
    justify="center"
).pack()

tk.Label(
    quote_frame,
    text="— Robert Swan",
    font=("Georgia", 10),
    fg=colors["text_light"],
    bg=colors["bg_dark"],
    justify="center"
).pack(pady=(10, 0))

# Right panel - Login/Register forms
right_panel = tk.Frame(main_frame, bg=colors["bg_light"], width=500)
right_panel.pack(side="right", fill="both", expand=True)

# Create frames for login and register
login_frame = tk.Frame(right_panel, bg=colors["bg_light"])
register_frame = tk.Frame(right_panel, bg=colors["bg_light"])

# === LOGIN FRAME ===
login_heading_label = tk.Label(
    login_frame, 
    text="Welcome Back", 
    font=("Segoe UI", 24, "bold"), 
    fg=colors["text_dark"], 
    bg=colors["bg_light"]
)
login_heading_label.pack(pady=(40, 5))

tk.Label(
    login_frame,
    text="Sign in to continue to your dashboard",
    font=("Segoe UI", 12),
    fg=colors["text_muted"],
    bg=colors["bg_light"]
).pack(pady=(0, 30))

# Username
username_frame = tk.Frame(login_frame, bg=colors["bg_light"])
username_frame.pack(fill="x", pady=10, padx=60)

tk.Label(
    username_frame, 
    text="Username", 
    font=("Segoe UI", 11), 
    bg=colors["bg_light"], 
    anchor="w"
).pack(anchor="w", pady=(0, 5))

# Username with icon
user_input_frame = tk.Frame(username_frame, bg=colors["bg_light"])
user_input_frame.pack(fill="x")

tk.Label(
    user_input_frame,
    text="👤",
    font=("Segoe UI", 14),
    bg=colors["bg_light"],
    fg=colors["primary"]
).pack(side="left", padx=(0, 5))

entry_username = ttk.Entry(user_input_frame, width=40, font=("Segoe UI", 11))
entry_username.pack(fill="x", ipady=5)

# Password
password_frame = tk.Frame(login_frame, bg=colors["bg_light"])
password_frame.pack(fill="x", pady=15, padx=60)

tk.Label(
    password_frame, 
    text="Password", 
    font=("Segoe UI", 11), 
    bg=colors["bg_light"], 
    anchor="w"
).pack(anchor="w", pady=(0, 5))

# Password with icon and toggle
pw_input_frame = tk.Frame(password_frame, bg=colors["bg_light"])
pw_input_frame.pack(fill="x")

tk.Label(
    pw_input_frame,
    text="🔒",
    font=("Segoe UI", 14),
    bg=colors["bg_light"],
    fg=colors["primary"]
).pack(side="left", padx=(0, 5))

entry_password = ttk.Entry(pw_input_frame, show="•", font=("Segoe UI", 11))
entry_password.pack(side="left", fill="x", expand=True, ipady=5)

toggle_btn = tk.Button(
    pw_input_frame,
    text="👁️",
    bg=colors["bg_light"],
    fg=colors["text_dark"],
    font=("Segoe UI", 12),
    bd=0,
    cursor="hand2",
    command=lambda: toggle_password(entry_password, toggle_btn)
)
toggle_btn.pack(side="right", padx=5)

# Remember me and forgot password
options_frame = tk.Frame(login_frame, bg=colors["bg_light"])
options_frame.pack(fill="x", pady=10, padx=60)

remember_var = tk.IntVar()
remember_check = ttk.Checkbutton(
    options_frame, 
    text="Remember me", 
    variable=remember_var,
    style="TCheckbutton"
)
remember_check.pack(side="left")

forgot_btn = tk.Label(
    options_frame, 
    text="Forgot password?", 
    fg=colors["primary"], 
    cursor="hand2", 
    bg=colors["bg_light"],
    font=("Segoe UI", 10, "underline")
)
forgot_btn.pack(side="right")

# Login button
login_btn = tk.Button(
    login_frame,
    text="Sign In",
    font=("Segoe UI", 12, "bold"),
    bg=colors["primary"],
    fg=colors["text_light"],
    padx=15,
    pady=10,
    width=20,
    bd=0,
    cursor="hand2",
    command=login_user
)
login_btn.pack(pady=25)

# Add hover effect
create_hover_effect(login_btn, colors["secondary"], colors["primary"])

# Sign up option
signup_frame = tk.Frame(login_frame, bg=colors["bg_light"])
signup_frame.pack(pady=20)

tk.Label(
    signup_frame,
    text="Don't have an account?",
    font=("Segoe UI", 10),
    bg=colors["bg_light"]
).pack(side="left")

signup_link = tk.Label(
    signup_frame,
    text="Create Account",
    fg=colors["primary"],
    cursor="hand2",
    font=("Segoe UI", 10, "bold"),
    bg=colors["bg_light"]
)
signup_link.pack(side="left", padx=5)
signup_link.bind("<Button-1>", lambda e: show_register_frame())

# === REGISTER FRAME ===
register_heading_label = tk.Label(
    register_frame, 
    text="Create an Account", 
    font=("Segoe UI", 24, "bold"), 
    fg=colors["text_dark"], 
    bg=colors["bg_light"]
)
register_heading_label.pack(pady=(40, 5))

tk.Label(
    register_frame,
    text="Join the wildlife conservation community",
    font=("Segoe UI", 12),
    fg=colors["text_muted"],
    bg=colors["bg_light"]
).pack(pady=(0, 30))

# Username for register
reg_username_frame = tk.Frame(register_frame, bg=colors["bg_light"])
reg_username_frame.pack(fill="x", pady=10, padx=60)

tk.Label(
    reg_username_frame,
    text="Username",
    font=("Segoe UI", 11),
    bg=colors["bg_light"],
    anchor="w"
).pack(anchor="w", pady=(0, 5))

# Username with icon
reg_user_input = tk.Frame(reg_username_frame, bg=colors["bg_light"])
reg_user_input.pack(fill="x")

tk.Label(
    reg_user_input,
    text="👤",
    font=("Segoe UI", 14),
    bg=colors["bg_light"],
    fg=colors["primary"]
).pack(side="left", padx=(0, 5))

entry_username_reg = ttk.Entry(reg_user_input, width=40, font=("Segoe UI", 11))
entry_username_reg.pack(fill="x", ipady=5)

# Password for register
reg_password_frame = tk.Frame(register_frame, bg=colors["bg_light"])
reg_password_frame.pack(fill="x", pady=15, padx=60)

tk.Label(
    reg_password_frame,
    text="Password",
    font=("Segoe UI", 11),
    bg=colors["bg_light"],
    anchor="w"
).pack(anchor="w", pady=(0, 5))

# Password with icon
reg_pw_input = tk.Frame(reg_password_frame, bg=colors["bg_light"])
reg_pw_input.pack(fill="x")

tk.Label(
    reg_pw_input,
    text="🔒",
    font=("Segoe UI", 14),
    bg=colors["bg_light"],
    fg=colors["primary"]
).pack(side="left", padx=(0, 5))

entry_password_reg = ttk.Entry(reg_pw_input, show="•", font=("Segoe UI", 11))
entry_password_reg.pack(side="left", fill="x", expand=True, ipady=5)

toggle_reg_btn = tk.Button(
    reg_pw_input,
    text="👁️",
    bg=colors["bg_light"],
    fg=colors["text_dark"],
    font=("Segoe UI", 12),
    bd=0,
    cursor="hand2",
    command=lambda: toggle_password(entry_password_reg, toggle_reg_btn)
)
toggle_reg_btn.pack(side="right", padx=5)

# Confirm password
reg_confirm_frame = tk.Frame(register_frame, bg=colors["bg_light"])
reg_confirm_frame.pack(fill="x", pady=15, padx=60)

tk.Label(
    reg_confirm_frame,
    text="Confirm Password",
    font=("Segoe UI", 11),
    bg=colors["bg_light"],
    anchor="w"
).pack(anchor="w", pady=(0, 5))

# Confirm with icon
reg_confirm_input = tk.Frame(reg_confirm_frame, bg=colors["bg_light"])
reg_confirm_input.pack(fill="x")

tk.Label(
    reg_confirm_input,
    text="🔒",
    font=("Segoe UI", 14),
    bg=colors["bg_light"],
    fg=colors["primary"]
).pack(side="left", padx=(0, 5))

entry_confirm = ttk.Entry(reg_confirm_input, show="•", font=("Segoe UI", 11))
entry_confirm.pack(side="left", fill="x", expand=True, ipady=5)

toggle_confirm_btn = tk.Button(
    reg_confirm_input,
    text="👁️",
    bg=colors["bg_light"],
    fg=colors["text_dark"],
    font=("Segoe UI", 12),
    bd=0,
    cursor="hand2",
    command=lambda: toggle_password(entry_confirm, toggle_confirm_btn)
)
toggle_confirm_btn.pack(side="right", padx=5)

# Register button
register_btn = tk.Button(
    register_frame,
    text="Create Account",
    font=("Segoe UI", 12, "bold"),
    bg=colors["primary"],
    fg=colors["text_light"],
    padx=15,
    pady=10,
    width=20,
    bd=0,
    cursor="hand2",
    command=register_user
)
register_btn.pack(pady=25)

# Add hover effect
create_hover_effect(register_btn, colors["secondary"], colors["primary"])

# Login option
login_option_frame = tk.Frame(register_frame, bg=colors["bg_light"])
login_option_frame.pack(pady=20)

tk.Label(
    login_option_frame,
    text="Already have an account?",
    font=("Segoe UI", 10),
    bg=colors["bg_light"]
).pack(side="left")

login_link = tk.Label(
    login_option_frame,
    text="Sign In",
    fg=colors["primary"],
    cursor="hand2",
    font=("Segoe UI", 10, "bold"),
    bg=colors["bg_light"]
)
login_link.pack(side="left", padx=5)
login_link.bind("<Button-1>", lambda e: show_login_frame())

# Start with login frame
show_login_frame()

# Add a footer
footer_frame = tk.Frame(root, bg="#f5f5f5", height=30)
footer_frame.pack(side="bottom", fill="x")

tk.Label(
    footer_frame,
    text=f"© {datetime.now().year} WildGuard Conservation | Protecting Wildlife Together",
    font=("Segoe UI", 8),
    fg="#666666",
    bg="#f5f5f5"
).pack(pady=8)

# Startup animation
def startup_animation():
    # Create a splash effect
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)
    overlay.attributes('-alpha', 1.0)
    overlay.configure(bg=colors["primary"])
    
    # Position over main window
    overlay.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{root.winfo_x()}+{root.winfo_y()}")
    
    # Add logo/text
    splash_frame = tk.Frame(overlay, bg=colors["primary"])
    splash_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # Logo label
    logo_label = tk.Label(
        splash_frame, 
        text="🐾", 
        font=("Segoe UI", 48), 
        fg="white", 
        bg=colors["primary"]
    )
    logo_label.pack()
    
    # App name with shorter delay
    def show_app_name():
        tk.Label(
            splash_frame, 
            text="WildGuard", 
            font=("Segoe UI", 24, "bold"), 
            fg="white", 
            bg=colors["primary"]
        ).pack()
    
    # Shorter delay (250ms vs 500ms)
    overlay.after(250, show_app_name)
    
    # Pulse animation - fewer pulses and faster
    def pulse(count=0):
        if count < 2:  # 2 pulses instead of 3
            logo_label.config(font=("Segoe UI", 52))
            overlay.after(150, lambda: logo_label.config(font=("Segoe UI", 48)))
            overlay.after(300, lambda: pulse(count+1))  # 300ms cycle vs 400ms
        else:
            start_fade_out()
    
    # Start the pulse effect sooner
    overlay.after(400, pulse)  # 400ms vs 800ms
    
    # Faster fade out (15 steps vs 25)
    def start_fade_out():
        for i in range(15, -1, -1):
            overlay.attributes('-alpha', i/15)
            overlay.update()
            time.sleep(0.03)  # 0.03s vs 0.05s
            
        overlay.destroy()

# Run startup animation after window appears
root.after(200, startup_animation)

root.mainloop()

# Close the connection when the application is closed
try:
    conn.close()
except:
    pass
