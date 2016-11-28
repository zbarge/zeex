import tkinter as tk
from tkinter import ttk



class MainTrix(ttk.Frame):
    def __init__(self, master=None):

        master.title("DBTrix")
            
        ttk.Frame.__init__(self, master)
        self.main_filepath = tk.StringVar(self)
        self.grid()
        self.create_widgets()
        
    def create_widgets(self):
        
        self.main_menu = tk.Menu(self)
        file_menu = tk.Menu(self.main_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Drop", command=self.drop_file)
        self.main_menu.add_cascade(label="File", menu=file_menu)
        
        action_menu = tk.Menu(self.main_menu)
        action_menu.add_command(label="Dedupe", command=self.dedupe_file)
        self.main_menu.add_cascade(label="Action", menu=action_menu)
        
        self.master.config(menu=self.main_menu)
        
        self.main_file_label = ttk.Label(self, text="Main File:")
        self.main_file_entry =  ttk.Entry(self, textvariable=self.main_filepath)
        
        self.main_file_label.grid(row=1, column=0)
        self.main_file_entry.grid(row=1, column=2)
        
    def open_file(self):
        self.main_filepath.set(tk.filedialog.askopenfilename())
        
    def drop_file(self):
        self.main_filepath.set("")
    def dedupe_file(self):
        pass
    

def main():
    root = tk.Tk()
    try:
        app = MainTrix(root)
        app.mainloop()
    finally:
        try:
            root.destroy()
        except:
            pass
    

if __name__ == "__main__":
    main()