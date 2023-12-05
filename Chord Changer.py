import os
import random
import time
import threading
from PIL import Image, ImageTk
import tkinter as tk

class ImageDisplayApp:
    def __init__(self, master):
        self.master = master
        master.title("Image Display App")

        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the images folder
        self.folder_path = os.path.join(current_directory, 'images')
        
        self.images_per_minute = 0
        self.running = False
        self.image_label = tk.Label(master)
        self.image_label.pack()

        self.info_label = tk.Label(master, text="Elapsed Time: 00:00 | Images Displayed: 0")
        self.info_label.pack()

        self.label = tk.Label(master, text="Enter the number of images to display per minute:")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.exclude_buttons_frame = tk.Frame(master)
        self.exclude_buttons_frame.pack()

        self.start_button = tk.Button(master, text="Start", command=self.start_display)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_display, state=tk.DISABLED)
        self.stop_button.pack()

        self.start_time = time.time()
        self.displayed_images = 0
        self.excluded_images = set()

    def display_images(self):
        image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]
        image_files = [f for f in image_files if f not in self.excluded_images]

        if not image_files:
            print("No image files found in the specified folder or all images are excluded.")
            return

        seconds_per_image = 60 / self.images_per_minute

        while self.running:
            image_name = random.choice(image_files)
            image_path = os.path.join(self.folder_path, image_name)

            try:
                image = Image.open(image_path)
                image.thumbnail((40, 50))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                displayed_image = Image.open(image_path)
                displayed_image = displayed_image.resize((200, 300)) 
                displayed_photo = ImageTk.PhotoImage(displayed_image)
                self.image_label.configure(image=displayed_photo)
                self.image_label.image = displayed_photo
                self.displayed_images += 1
                elapsed_time = time.strftime("%M:%S", time.gmtime(time.time() - self.start_time))
                info_text = f"Elapsed Time: {elapsed_time} | Images Displayed: {self.displayed_images}"
                self.info_label.config(text=info_text)
            except IOError:
                print(f"Unable to load image: {image_name}")

            time.sleep(seconds_per_image)

    def exclude_image(self, image_name):
        self.excluded_images.add(image_name)
        self.update_exclude_buttons()

    def update_exclude_buttons(self):
        for widget in self.exclude_buttons_frame.winfo_children():
            widget.destroy()

        image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]
        for image_name in image_files:
            if image_name not in self.excluded_images:
                try:
                    image = Image.open(os.path.join(self.folder_path, image_name))
                    image.thumbnail((40, 50))  # Adjust the thumbnail size as needed
                    photo = ImageTk.PhotoImage(image)
                    button_name = os.path.splitext(image_name)[0]  # Remove the extension
                    button = tk.Button(self.exclude_buttons_frame, image=photo, text=button_name, command=lambda name=image_name: self.exclude_image(name), compound=tk.TOP)
                    button.image = photo  # Store a reference to prevent garbage collection
                    button.pack(side=tk.LEFT)
                except IOError:
                    print(f"Unable to load image: {image_name}")

    def start_display(self):
        try:
            self.images_per_minute = int(self.entry.get())
        except ValueError:
            print("Please enter a valid number.")
            return

        if self.images_per_minute <= 0:
            print("Please enter a number greater than zero.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.start_time = time.time()
        self.displayed_images = 0

        self.update_exclude_buttons()

        display_thread = threading.Thread(target=self.display_images)
        display_thread.start()

    def stop_display(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDisplayApp(root)
    root.mainloop()

