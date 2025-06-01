# ================= AUTH_SETUP.PY (Polished + Modern UI with Signup and Transitions Support) =================
import tkinter as tk
from tkinter import ttk
import sqlite3
import hashlib
import sys
# Database functions
def connect_db():
    return sqlite3.connect("users.db")

def setup():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == hash_password(password)

class App:
    def __init__(self, root, server_socket):
        self.client_socket = server_socket
        self.root = root
        self.root.title("STICK FIGHT - Auth")
        self.root.geometry("1280x720")
        self.root.configure(bg="#FFFFFF")

        self.bg_color = "#FFFFFF"
        self.accent_color = "#6C63FF"
        self.text_color = "#333333"
        self.placeholder_color = "#AAAAAA"

        self.logged_in_username = ""
        self.logged_in_password = ""
        self.login_success = False  # <- NEW FLAG

        self.frame = tk.Frame(self.root, bg=self.bg_color)
        self.frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.is_login = True
        self.build_form()

    def build_form(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        mode_text = "Login" if self.is_login else "Sign Up"
        sub_text = "Login to your account" if self.is_login else "Create a new account"

        tk.Label(self.frame, text="STICK FIGHT", font=("Helvetica", 24, "bold"), fg=self.accent_color, bg=self.bg_color).pack(pady=(0, 10))
        tk.Label(self.frame, text=sub_text, font=("Helvetica", 12), fg=self.placeholder_color, bg=self.bg_color).pack(pady=(0, 20))

        self.username_entry = self.create_modern_entry("Username")
        self.password_entry = self.create_modern_entry("Password", show="*")

        self.message_label = tk.Label(self.frame, text="", fg="red", bg=self.bg_color, font=("Helvetica", 10))
        self.message_label.pack(pady=10)

        action_text = "LOG IN" if self.is_login else "SIGN UP"
        action_command = self.login_user if self.is_login else self.signup_user

        self.action_button = tk.Button(
            self.frame, text=action_text, font=("Helvetica", 12, "bold"),
            bg=self.accent_color, fg="#FFFFFF", activebackground="#5A52CC",
            relief="flat", borderwidth=0, padx=20, pady=12,
            cursor="hand2", command=action_command
        )
        self.action_button.pack(pady=(10, 5), fill="x")

        switch_text = "Don't have an account? Sign up" if self.is_login else "Already have an account? Log in"
        switch = tk.Label(self.frame, text=switch_text, font=("Helvetica", 10), fg=self.accent_color, bg=self.bg_color, cursor="hand2")
        switch.pack()
        switch.bind("<Button-1>", lambda e: self.toggle_mode())

    def toggle_mode(self):
        self.is_login = not self.is_login
        self.build_form()

    def create_modern_entry(self, placeholder, show=None):
        frame = tk.Frame(self.frame, bg=self.bg_color)
        frame.pack(fill="x", pady=10)

        tk.Label(frame, text=placeholder, font=("Helvetica", 11), fg=self.text_color, bg=self.bg_color).pack(fill="x", anchor="w")

        entry_frame = tk.Frame(frame, bg="#EEEEEE", highlightbackground="#E0E0E0", highlightthickness=1)
        entry_frame.pack(fill="x")

        entry = tk.Entry(
            entry_frame, font=("Helvetica", 11), bg="#EEEEEE", fg=self.text_color,
            bd=0, insertbackground=self.text_color, show=show
        )
        entry.pack(fill="x", ipady=8, ipadx=10)
        entry.insert(0, placeholder)
        entry.config(fg=self.placeholder_color)

        entry.bind("<FocusIn>", lambda e: self._on_entry_focus_in(entry, placeholder, show))
        entry.bind("<FocusOut>", lambda e: self._on_entry_focus_out(entry, placeholder, show))

        entry.bind("<FocusIn>", lambda e: entry_frame.config(highlightbackground=self.accent_color), add="+")
        entry.bind("<FocusOut>", lambda e: entry_frame.config(highlightbackground="#E0E0E0"), add="+")

        return entry

    def _on_entry_focus_in(self, entry, placeholder, show):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=self.text_color)
            if show:
                entry.config(show=show)

    def _on_entry_focus_out(self, entry, placeholder, show):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg=self.placeholder_color)
            if show:
                entry.config(show="")

    def login_user(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if user in ("", "Username") or pwd in ("", "Password"):
            self.message_label.config(text="Please fill in all fields", fg="red")
            return

        self.action_button.config(state="disabled")
        self.message_label.config(text="Logging in...", fg="grey")
        self.frame.update()

        if login(user, pwd):
            self.logged_in_username = user
            self.logged_in_password = pwd
            self.client_socket.send(f"LOGIN {user} {pwd}".encode())
            self.login_success = True  # <- NEW FLAG
            self.root.destroy()
        else:
            self.message_label.config(text="Invalid credentials", fg="red")
            self.action_button.config(state="normal")

    def signup_user(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if user in ("", "Username") or pwd in ("", "Password"):
            self.message_label.config(text="Please fill in all fields", fg="red")
            return

        self.action_button.config(state="disabled")
        self.message_label.config(text="Creating account...", fg="grey")
        self.frame.update()

        if register(user, pwd):
            self.message_label.config(text="Account created! You can log in now.", fg="green")
            self.toggle_mode()
        else:
            self.message_label.config(text="Username already exists", fg="red")
            self.action_button.config(state="normal")

    def get_login_user_n_password(self):
        return self.logged_in_username, self.logged_in_password

if __name__ == "__main__":
    setup()
    root = tk.Tk()
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5555))
    app = App(root, sock)
    root.mainloop()
