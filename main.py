import requests
import json
import ctypes
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import subprocess
import glob

# config file
CONFIG_FILE = "config.json"

# load config
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"download_directory": os.path.expanduser("~")}

# save config
def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# default directory for saving wallpapers
config = load_config()
download_directory = config["download_directory"]

# global variables for pagination
current_page = 0
posts = []

def change_directory():
    global download_directory
    new_directory = filedialog.askdirectory()
    if new_directory:
        download_directory = new_directory
        directory_label.config(text=f"Download Directory: {download_directory}")
        config["download_directory"] = download_directory
        save_config(config)

def open_directory():
    subprocess.Popen(f'explorer "{os.path.realpath(download_directory)}"')

def delete_wallpapers():
    for file in glob.glob(os.path.join(download_directory, "wallpaper_*.jpg")):
        os.remove(file)
    messagebox.showinfo("Success", "All wallpaper files have been deleted.")

def fetch_images():
    global posts, current_page
    subreddit_url = entry.get().strip()
    section = section_var.get()
    
    if not subreddit_url.endswith('/'):
        subreddit_url += '/'
    subreddit_url += f'{section}.json'

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"}
    response = requests.get(subreddit_url, headers=headers)

    if response.status_code == 429:
        messagebox.showerror("Error", "Too Many Requests. Please try again later.")
        return

    try:
        jsonData = response.json()
        posts = jsonData.get("data", {}).get("children", [])
        if not posts:
            messagebox.showerror("Error", "No posts found.")
        else:
            current_page = 0
            display_images()
    except (KeyError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Failed to decode JSON response: {e}")

def display_images():
    global posts, current_page
    for widget in image_frame.winfo_children():
        widget.destroy()

    start = current_page * 5
    end = start + 5
    valid_images = 0
    i = start

    while valid_images < 5 and i < len(posts):
        post = posts[i]
        image_url = post["data"]["url"]
        try:
            imageContents = requests.get(image_url).content
            image = Image.open(io.BytesIO(imageContents))
            image.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(image)

            button = tk.Button(image_frame, image=photo, command=lambda url=image_url: set_wallpaper(url))
            button.image = photo
            button.grid(row=0, column=valid_images, padx=5, pady=5)
            valid_images += 1
        except UnidentifiedImageError:
            print(f"Skipping non-image URL: {image_url}")
        i += 1

    if valid_images > 0:
        pagination_frame.pack(pady=5)
        prev_button.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
        next_button.config(state=tk.NORMAL if end < len(posts) else tk.DISABLED)
    else:
        pagination_frame.pack_forget()

def set_wallpaper(image_url):
    imageContents = requests.get(image_url).content

    # find the next available filename
    i = 0
    while os.path.exists(os.path.join(download_directory, f"wallpaper_{i}.jpg")):
        i += 1
    wallpaper_path = os.path.join(download_directory, f"wallpaper_{i}.jpg")

    with open(wallpaper_path, "wb") as imageFile:
        imageFile.write(imageContents)

    if os.path.exists(wallpaper_path):
        print(f"Image downloaded successfully to {wallpaper_path}")
        SPI_SETDESKWALLPAPER = 20
        result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)
        if result:
            messagebox.showinfo("Success", "Wallpaper set successfully.")
        else:
            messagebox.showerror("Error", f"Failed to set wallpaper. Error code: {ctypes.GetLastError()}")
    else:
        messagebox.showerror("Error", "Failed to download image.")

def next_page():
    global current_page
    current_page += 1
    display_images()

def prev_page():
    global current_page
    current_page -= 1
    display_images()

# create main window
root = tk.Tk()
root.title("Reddit Wallpaper Downloader")

# create and place widgets
label = tk.Label(root, text="Enter Subreddit URL:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

section_var = tk.StringVar(value="hot")
section_label = tk.Label(root, text="Select Section:")
section_label.pack(pady=5)

section_menu = ttk.Combobox(root, textvariable=section_var, values=["hot", "top", "new"], state="readonly")
section_menu.pack(pady=5)

fetch_button = tk.Button(root, text="Fetch Images", command=fetch_images)
fetch_button.pack(pady=20)

directory_label = tk.Label(root, text=f"Download Directory: {download_directory}")
directory_label.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

change_directory_button = tk.Button(button_frame, text="Change Directory", command=change_directory)
change_directory_button.pack(side=tk.LEFT, padx=5)

open_directory_button = tk.Button(button_frame, text="Open Directory", command=open_directory)
open_directory_button.pack(side=tk.LEFT, padx=5)

delete_wallpapers_button = tk.Button(button_frame, text="Delete Wallpapers", command=delete_wallpapers)
delete_wallpapers_button.pack(side=tk.LEFT, padx=5)

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

pagination_frame = tk.Frame(root)

prev_button = tk.Button(pagination_frame, text="Previous", command=prev_page)
prev_button.pack(side=tk.LEFT, padx=5)

next_button = tk.Button(pagination_frame, text="Next", command=next_page)
next_button.pack(side=tk.LEFT, padx=5)

# run application
root.mainloop()