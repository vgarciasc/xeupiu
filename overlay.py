import time
import tkinter as tk

bg_img = None

class OverlayWindow:
    def __init__(self, x_pos=None, y_pos=None):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.8)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        # Get the screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Set the window size and position it at the bottom center
        self.window_width = 520  # Adjust as needed
        self.window_height = 105  # Adjust as needed
        self.x_pos = x_pos if x_pos else (self.screen_width - self.window_width) // 2
        self.y_pos = y_pos if y_pos else self.screen_height - self.window_height * 3

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_pos}+{self.y_pos}")

        global bg_img
        bg_img = tk.PhotoImage(file="data/emerald_bg.png")

        # self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height)
        # self.canvas.create_image(0, 0, image=bg_img, anchor='nw')
        # self.canvas.pack(expand=True, fill='both')

        self.label = tk.Label(self.root, text="asdf", font=("Arial", 16), fg='white',
                              wraplength=self.window_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack(expand=True, fill='both')


    def update(self, new_text):
        self.label.config(text=new_text)
        self.root.update_idletasks()
        self.root.update()

    def update_text(self, new_text):
        self.label.config(text=new_text)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    overlay = OverlayWindow()

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " * 5)
        time.sleep(0.1)