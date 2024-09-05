import ctypes
import tkinter as tk
from tkinter import scrolledtext, ttk
import sys
from app import App
from config import CONFIG


class StdoutRedirector:
    def __init__(self, text_area):
        self.text_area = text_area
        self.original_stdout = sys.stdout
        sys.stdout = self

    def write(self, message):
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)

    def flush(self):
        pass

    def restore(self):
        sys.stdout = self.original_stdout

class XeupiuControlPanel:
    def __init__(self):
        self.app = None
        self.received_stop_signal = False

        # Create main window
        root = tk.Tk()
        root.title(f"XEUPIU {CONFIG['version']}")
        root.resizable(False, False)
        root.iconbitmap("data/resources/icon.ico")

        window_width = 1024
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        # Set the geometry to center the window
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Create frames for left and right panels
        left_frame = tk.Frame(root, width=10)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        # left_frame.grid_columnconfigure(0, weight=1)
        # left_frame.grid_columnconfigure(1, weight=1)

        right_frame = tk.Frame(root, width=40)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # right_frame.grid_columnconfigure(0, weight=1)
        # right_frame.grid_columnconfigure(1, weight=1)

        # Left panel - Input fields
        jp_name_var = tk.StringVar(value=CONFIG['save']['player']['jp_name'])
        jp_surname_var = tk.StringVar(value=CONFIG['save']['player']['jp_surname'])
        jp_nickname_var = tk.StringVar(value=CONFIG['save']['player']['jp_nickname'])
        en_name_var = tk.StringVar(value=CONFIG['save']['player']['en_name'])
        en_surname_var = tk.StringVar(value=CONFIG['save']['player']['en_surname'])
        en_nickname_var = tk.StringVar(value=CONFIG['save']['player']['en_nickname'])
        deepL_key_var = tk.StringVar(value=CONFIG['translation']['deepl']['api_key'])

        image = tk.PhotoImage(file="data/resources/logo.png")
        tk.Label(left_frame, image=image).grid(row=0, column=0, columnspan=2, sticky=tk.N)

        tk.Label(left_frame, text="Japanese surname:").grid(row=2, column=0, sticky=tk.W)
        self.jp_surname_entry = tk.Entry(left_frame, textvariable=jp_surname_var, state="disabled")
        self.jp_surname_entry.grid(row=2, column=1, sticky=tk.E)

        tk.Label(left_frame, text="Japanese name:").grid(row=3, column=0, sticky=tk.W)
        self.jp_name_entry = tk.Entry(left_frame, textvariable=jp_name_var, state="disabled")
        self.jp_name_entry.grid(row=3, column=1, sticky=tk.E)

        tk.Label(left_frame, text="Japanese nickname:").grid(row=4, column=0, sticky=tk.W)
        self.jp_nickname_entry = tk.Entry(left_frame, textvariable=jp_nickname_var, state="disabled")
        self.jp_nickname_entry.grid(row=4, column=1, sticky=tk.E)

        tk.Label(left_frame, text="English name:").grid(row=5, column=0, sticky=tk.W)
        self.en_name_entry = tk.Entry(left_frame, textvariable=en_name_var)
        self.en_name_entry.grid(row=5, column=1, sticky=tk.E)

        tk.Label(left_frame, text="English surname:").grid(row=6, column=0, sticky=tk.W)
        self.en_surname_entry = tk.Entry(left_frame, textvariable=en_surname_var)
        self.en_surname_entry.grid(row=6, column=1, sticky=tk.E)

        tk.Label(left_frame, text="English nickname:").grid(row=7, column=0, sticky=tk.W)
        self.en_nickname_entry = tk.Entry(left_frame, textvariable=en_nickname_var)
        self.en_nickname_entry.grid(row=7, column=1, sticky=tk.E)

        tk.Label(left_frame, text="DeepL Key:").grid(row=8, column=0, sticky=tk.W)
        self.deepL_key_entry = tk.Entry(left_frame, textvariable=deepL_key_var, show="*")
        self.deepL_key_entry.grid(row=8, column=1, sticky=tk.E)

        tk.Label(left_frame, text="Verbose level:").grid(row=9, column=0, sticky=tk.W)
        self.verbose_var = tk.IntVar(value=CONFIG['verbose_level'])
        self.verbose_entry = tk.Entry(left_frame, textvariable=self.verbose_var)
        self.verbose_entry.grid(row=9, column=1, sticky=tk.E)

        tk.Label(left_frame, text="History size:").grid(row=10, column=0, sticky=tk.W)
        self.history_size_var = tk.IntVar(value=CONFIG['history_size'])
        self.history_size_entry = tk.Entry(left_frame, textvariable=self.history_size_var)
        self.history_size_entry.grid(row=10, column=1, sticky=tk.E)

        self.fullscreen_var = tk.IntVar(value=CONFIG['fullscreen'])
        self.fullscreen_checkbox = tk.Checkbutton(left_frame, text="Fullscreen", variable=self.fullscreen_var)
        self.fullscreen_checkbox.grid(row=11, column=0, columnspan=2, sticky=tk.W)

        self.run_button = tk.Button(left_frame, text="Save and run", command=self.save_and_run, width=15)
        self.run_button.grid(row=12, column=0, pady=5, sticky=tk.E)

        self.exit_button = tk.Button(left_frame, text="Close app", command=self.close, width=15)
        self.exit_button.grid(row=12, column=1, pady=5, padx=5, sticky=tk.W)
        self.exit_button.config(state="disabled")

        self.log_button = tk.Button(left_frame, text="(DEBUG) Log everything", command=self.log_everything)
        self.log_button.grid(row=13, column=0, columnspan=2, pady=5)

        separator = ttk.Separator(left_frame, orient="horizontal")
        separator.grid(row=14, columnspan=2, pady=10, sticky="ew")

        notes_label = tk.Label(left_frame, text="NOTES:", font=("Arial", 10, "bold"))
        notes_label.grid(row=15, column=0, columnspan=2, sticky=tk.W)

        notes_text = tk.Label(left_frame, text='1. When creating your save, please make sure to input the japanese '
                                               'name, surname, and nickname displayed above. This will guarantee that '
                                               'the tool is able to detect them correctly. Fill the English fields '
                                               'with your desired names you want to use in the game.\n\n'
                                               '2. At the current phase of the project, a valid DeepL Key is required '
                                               'for the translation of the game. Please make sure to input a valid key '
                                               '-- the free ones are more than enough to play through the game multiple '
                                               'times. Visit the DeepL website for more information.\n\n'
                                               '3. If you encounter any problems, please read the FAQ in the ' 
                                               'XEUPIU GitHub repository.\n\n'
                                               '4. Enjoy the game!',
                              wraplength=0.3*window_width, justify=tk.LEFT)
        notes_text.grid(row=16, column=0, columnspan=2, sticky=tk.W)

        separator = ttk.Separator(left_frame, orient="horizontal")
        separator.grid(row=17, columnspan=2, pady=10, sticky="ew")

        notes_label = tk.Label(left_frame, text=f"XEUPIU {CONFIG['version']}\n"
                                                f"typed in brazil by vinizinho, 2024", font=("Courier", 10, "italic"))
        notes_label.grid(row=18, column=0, columnspan=2, sticky=tk.N)

        # Right panel - Text area
        self.output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, bg="black", height=50,
                                                     fg="white", font=("MS Gothic", 12))
        self.output_text.pack()

        # Redirect stdout to the text area
        stdout_redirector = StdoutRedirector(self.output_text)

        # Start main loop
        root.mainloop()

        # Restore original stdout
        stdout_redirector.restore()

    def save_and_run(self):
        CONFIG['save']['player']['en_name'] = self.en_name_entry.get()
        CONFIG['save']['player']['en_surname'] = self.en_surname_entry.get()
        CONFIG['save']['player']['en_nickname'] = self.en_nickname_entry.get()
        CONFIG['fullscreen'] = bool(self.fullscreen_var.get())
        CONFIG['verbose_level'] = self.verbose_var.get()
        CONFIG['history_size'] = self.history_size_var.get()
        CONFIG['translation']['deepl']['api_key'] = self.deepL_key_entry.get()

        self.jp_name_entry.config(state="disabled")
        self.jp_surname_entry.config(state="disabled")
        self.jp_nickname_entry.config(state="disabled")
        self.en_name_entry.config(state="disabled")
        self.en_surname_entry.config(state="disabled")
        self.en_nickname_entry.config(state="disabled")
        self.deepL_key_entry.config(state="disabled")
        self.verbose_entry.config(state="disabled")
        self.history_size_entry.config(state="disabled")
        self.fullscreen_checkbox.config(state="disabled")
        self.run_button.config(state="disabled")
        self.exit_button.config(state="active")

        if self.deepL_key_entry.get() == "":
            ctypes.windll.user32.MessageBoxW(0, "DeepL key is not set. If any novel text is encountered, the tool "
                                                "will quit. Be aware!", "Project XEUPIU - Error!", 0x40000)

        try:
            self.app = App()
            while not self.received_stop_signal:
                self.app.step()

                # current_lines = int(self.output_text.index('end-1c').split('.')[0])
                # if current_lines > CONFIG['cmd_max_lines']:
                #     self.output_text.delete('1.0', f"{current_lines - CONFIG['cmd_max_lines'] + 1}.0")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.close()

    def close(self):
        print("Exiting...")
        self.received_stop_signal = True
        sys.exit(0)
        # self.exit_button.config(state="disabled")
        # self.run_button.config(state="active")
        # self.app.close()

    def log_everything(self):
        print_history = self.output_text.get("1.0", 'end-1c')
        if self.app is not None:
            self.app.log_everything(print_history=print_history)

if __name__ == "__main__":
    xcp = XeupiuControlPanel()
