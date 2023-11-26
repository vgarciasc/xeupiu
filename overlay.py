import time
import tkinter as tk

bg_img = None


class OverlayWindow:
    def __init__(self, x_pos: int = 600, y_pos: int = 100):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.9)  # Make the window semi-transparent
        self.root.attributes("-topmost", True)  # Make the window semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations (border, title bar)

        # Get the screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Set the window size and position it at the bottom center
        self.window_width = 520  # Adjust as needed
        self.window_height = 105  # Adjust as needed
        self.x_pos = x_pos - self.window_width // 2 + 53
        self.y_pos = y_pos - self.window_height // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x_pos}+{self.y_pos}")

        global bg_img
        bg_img = tk.PhotoImage(file="data/emerald_bg.png")

        # self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height)
        # self.canvas.create_image(0, 0, image=bg_img, anchor='nw')
        # self.canvas.pack(expand=True, fill='both')

        # self.text = self.canvas.create_text(10, 10, anchor="nw", text="Hello", font=("Verdana", 16),
        #                                     fill='white', width=self.window_width, justify='left')
        #
        # self.text.insert("insert", "Hello")
        # self.text.insert("insert", " World!")
        # self.text.tag_add("start", "1.0", "1.5")
        # self.text.tag_config("start", foreground="red")
        # self.text.pack(expand=True, fill='both')

        self.label = tk.Label(self.root, text="asdf", font=("MS Pgothic", 16), fg='white',
                              wraplength=self.window_width, justify='left',
                              image=bg_img, compound='center')
        self.label.pack()


    def update(self, new_text: str, char_name: str = None) -> None:
        if char_name:
            new_text = char_name + "\n  " + new_text + ""

        self.label.config(text=new_text)

        # self.text.delete("1.0", "end")
        # self.text.insert("insert", new_text)

        self.root.update_idletasks()
        self.root.update()

    def update_text(self, new_text: str) -> None:
        self.label.config(text=new_text)

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    overlay = OverlayWindow()

    for _ in range(1000):
        overlay.update(time.strftime("%H:%M:%S") + " lorem ipsum dorem sit amet " *1, None)
        time.sleep(0.1)
