
import tkinter as tk
from PIL import Image, ImageTk
import os


class ImageGallery:

    def __init__(self, parent):

        self.window = tk.Toplevel(parent)
        self.window.title("HandFrame AI | Image Gallery")
        self.window.geometry("900x650")
        self.window.configure(bg="#101827")

        self.thumbnail_references = []

        title = tk.Label(
            self.window,
            text="IMAGE GALLERY",
            font=("Segoe UI", 20, "bold"),
            bg="#1B2638",
            fg="white",
            pady=15
        )
        title.pack(fill="x")

        self.canvas = tk.Canvas(
            self.window,
            bg="#101827",
            highlightthickness=0
        )
        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            self.window,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.gallery_frame = tk.Frame(
            self.canvas,
            bg="#101827"
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.gallery_frame,
            anchor="nw"
        )

        self.gallery_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.update_canvas_width
        )

        self.load_images()

    def update_scroll_region(self, event=None):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def update_canvas_width(self, event):

        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    def load_images(self):

        folders = [
            ("Captured Photos", "captured_images"),
            ("Edited Photos", "generated_images")
        ]

        row = 0

        for section_name, folder in folders:

            heading = tk.Label(
                self.gallery_frame,
                text=section_name,
                font=("Segoe UI", 15, "bold"),
                bg="#101827",
                fg="#72B7FF"
            )

            heading.grid(
                row=row,
                column=0,
                columnspan=3,
                sticky="w",
                padx=20,
                pady=(20, 10)
            )

            row += 1

            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

            files = [
                file for file in os.listdir(folder)
                if file.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                )
            ]

            files.sort(reverse=True)

            if not files:

                empty_label = tk.Label(
                    self.gallery_frame,
                    text="No images found.",
                    font=("Segoe UI", 10),
                    bg="#101827",
                    fg="#AAB8CA"
                )

                empty_label.grid(
                    row=row,
                    column=0,
                    columnspan=3,
                    padx=20,
                    pady=10,
                    sticky="w"
                )

                row += 1
                continue

            for index, filename in enumerate(files):

                image_path = os.path.join(
                    folder,
                    filename
                )

                try:

                    image = Image.open(image_path)
                    image.thumbnail(
                        (200, 140),
                        Image.Resampling.LANCZOS
                    )

                    photo = ImageTk.PhotoImage(image)
                    self.thumbnail_references.append(photo)

                    card = tk.Frame(
                        self.gallery_frame,
                        bg="#1B2638",
                        padx=8,
                        pady=8
                    )

                    card.grid(
                        row=row + index // 3,
                        column=index % 3,
                        padx=12,
                        pady=10
                    )

                    image_label = tk.Label(
                        card,
                        image=photo,
                        bg="#1B2638"
                    )
                    image_label.pack()

                    name_label = tk.Label(
                        card,
                        text=filename,
                        font=("Segoe UI", 8),
                        bg="#1B2638",
                        fg="white",
                        wraplength=190
                    )
                    name_label.pack(pady=(6, 0))

                    image_label.bind(
                        "<Button-1>",
                        lambda event, path=image_path:
                        self.open_image(path)
                    )

                except Exception as error:
                    print(
                        "Could not load image:",
                        filename,
                        error
                    )

            row += (len(files) + 2) // 3

    def open_image(self, image_path):

        try:

            image = Image.open(image_path)
            image.thumbnail((750, 550))

            preview_window = tk.Toplevel(self.window)
            preview_window.title("Image Preview")
            preview_window.configure(bg="#101827")

            photo = ImageTk.PhotoImage(image)

            label = tk.Label(
                preview_window,
                image=photo,
                bg="#101827"
            )
            label.image = photo
            label.pack(padx=15, pady=15)

        except Exception as error:

            print("Could not open image:", error)
