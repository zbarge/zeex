import os
import logging
import tkinter as tk
from tkinter import ttk
from dataframe import DataFrameManager
from fieldnames import FieldNames
from compat import string_to_list, string_to_bool
from config import config
from tkinter import messagebox as tkMessageBox


logger = logging.getLogger(__name__)
log_path = os.path.join(config['DATA_DIR'], "gui_log.log")

logging.FileHandler(log_path)


class FieldEditor(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.db = FieldNames()
        self.old_name = tk.StringVar(self)
        self.new_name = tk.StringVar(self)
        self.title("Field Definitions Editor")
        self.configure_widgets()
        
    def configure_widgets(self):
        
        self.old_label = ttk.Label(self, text="Old Name")
        self.new_label = ttk.Label(self, text="New Name")
        self.old_entry = ttk.Entry(self, textvariable=self.old_name)
        self.new_entry = ttk.Entry(self, textvariable=self.new_name)
        self.add_button = ttk.Button(self, text="Add", command=self.add_entry)
        self.delete_button = ttk.Button(self, text="Delete", command=self.delete_entry)
        self.rename_button = ttk.Button(self, text="Rename File", command=self.build_renames)
        
        self.tree = ttk.Treeview(self, columns=("Original Name", "New Name", "Source"))
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading("#0", text="Item ID")
        self.tree.heading("#1", text="Original Name")
        self.tree.heading("#2", text="New Name")
        self.tree.heading("#3", text="Source")
        
        entries = self.db.session.query(self.db.Field).all()
        for entry in entries:
            self.insert_entry(entry)
        
        self.old_label.grid(row=0, column=0)
        self.old_entry.grid(row=0, column=1)
        self.new_label.grid(row=1, column=0)
        self.new_entry.grid(row=1, column=1)
        self.add_button.grid(row=2, column=0)
        self.delete_button.grid(row=2, column=1)
        self.rename_button.grid(row=2, column=3)
        self.tree.grid(row=4,column=0, columnspan=4)
        ysb.grid(row=4, column=5, sticky='ns')
        xsb.grid(row=5, column=0, columnspan=5, sticky='ew')    
        
    def add_entry(self):
        old_name = self.old_name.get()
        new_name = self.new_name.get()
        source = "User Input"
        try:
            entry = self.db.add_entry(old_name, new_name, source)
        except Exception as e:
            self.db.session.rollback()
            tkMessageBox.showerror("Error adding Entry", e)
            raise
        self.insert_entry(entry)
            
    def delete_entry(self):
        idx = self.tree.focus()
        item = self.tree.item(idx)
        old_name = item['values'][0]
        self.db.delete_entry(old_name)
        self.tree.delete(idx)
        tkMessageBox.showinfo("Deleted Entry", "Entry {} was deleted!".format(old_name))
        
    def insert_entry(self, entry):
        self.tree.insert("", 
                 'end', 
                 iid=entry.id, 
                 text=entry.id,
                 values=(entry.orig_name, entry.new_name, entry.source))
        
    def build_renames(self, df=None):
        if df is None:
            df = self.master.framer.read_file(self.master.main_filepath.get())
            
        renames = self.db.get_renames(df.columns)
        rename_wdw = tk.Toplevel(self)
        menu = tk.Menu(rename_wdw)
        
        row_id = 0
        entries = []
        
        for old_name, new_name in renames.items():
            old_label = ttk.Label(rename_wdw, text=old_name)
            new_var = tk.StringVar(rename_wdw, new_name)
            new_entry = ttk.Entry(rename_wdw, textvariable=new_var)
            old_label.grid(column=0, row=row_id)
            new_entry.grid(column=1, row=row_id)
            entries.append([old_name, new_var])
            row_id += 1
            
        def apply():
            for old_name, new_entry in entries:
                value = new_entry.get()
                print("old name: {}, new name:{}".format(old_name, value))
                
        menu.add_command(label="Update", command=apply)
        menu.master.config(menu=menu)
        
            
            
        
        
        
        

class MainTrix(ttk.Frame):
    
    def __init__(self, master=None):

        master.title("DBTrix")
            
        ttk.Frame.__init__(self, master)
        self.main_filepath = tk.StringVar(self)
        self.framer = DataFrameManager()
        self.grid()
        self.create_widgets()
        
    def create_widgets(self):
        
        self.main_menu = tk.Menu(self)
        
        file_menu = tk.Menu(self.main_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Drop", command=self.drop_file)
        self.main_menu.add_cascade(label="File", menu=file_menu)
        
        
        action_menu = tk.Menu(self.main_menu)
        action_menu.add_command(label="Dedupe", command=self.dedupe_file)
        action_menu.add_command(label="Sort", command=self.sort_file)
        action_menu.add_command(label="Suppress", command=self.suppress_file)
        action_menu.add_command(label="Merge", command=self.merge_file)
        action_menu.add_command(label="Split", command=self.split_file)
        action_menu.add_command(label="Update", command=self.update_file)
        action_menu.add_command(label="Rename", command=self.rename_file)
        self.main_menu.add_cascade(label="Action", menu=action_menu)
        self.main_menu.add_command(label="Field Definitions", command=self.view_field_defs)
        
        
        self.master.config(menu=self.main_menu)
        
        self.main_file_label = ttk.Label(self, text="Main File:")
        self.main_file_entry =  ttk.Entry(self, textvariable=self.main_filepath)
        
        self.main_file_label.grid(row=1, column=0)
        self.main_file_entry.grid(row=1, column=2)
        
    def open_file(self):
        self.main_filepath.set(tk.filedialog.askopenfilename())
        
    def drop_file(self):
        fp = self.main_filepath.get()
        self.main_filepath.set("")
        self.framer.remove_file(fp)
        logger.info("Removed file: {}".format(fp))
        
    def save_file(self):
        fp = self.main_filepath.get()
        self.framer.save_file(fp)
        logger.info("Saved file: {}".format(fp))
        
    def dedupe_file(self):
        pass
    
    def sort_file(self):
        """
        Generates new window
        with entry options for how to sort the file.
        Sorts the dataframe based on specified options.
        
        """
        
        
        sframe = tk.Toplevel(self)
        
        fields = tk.StringVar(sframe)
        asc = tk.StringVar(sframe)
        
        field_label = ttk.Label(sframe, text="Sort Fields:")        
        asc_label = ttk.Label(sframe, text="Ascending")
        
        field_entry = ttk.Entry(sframe, textvariable=fields)
        asc_entry = ttk.Entry(sframe, textvariable=asc)
        
        field_label.grid(row=0, column=0)
        field_entry.grid(row=0, column=1)
        
        asc_label.grid(row=1, column=0)
        asc_entry.grid(row=1, column=1)

        def execute_sort():
            filepath = self.main_filepath.get()
            logger.info("Sorting {}".format(filepath))
            df = self.framer.read_file(filepath)
            on = string_to_list(fields.get())
            ascending = string_to_list(asc.get())
            ascending = [string_to_bool(x) for x in ascending]
            notes = "Sorted data: on='{}', ascending='{}'".format(on, ascending)
            
            logger.info(notes)
            
            try:
                df.sort_values(on, ascending=ascending, inplace=True)
            except KeyError as e:
                msg = "KeyError on {}, Columns available: {}".format(e, df.columns)
                logger.warning(msg)
                raise KeyError(msg)
                
            self.framer.update_file(filepath, df, notes=notes)

            
        execute_btn = ttk.Button(sframe, text="Execute", command=execute_sort)
        execute_btn.grid(row=2, column=0)

        
    
    def suppress_file(self):
        pass    
    
    def merge_file(self):
        pass   
    
    def split_file(self):
        pass
    
    def update_file(self):
        pass
        
    def rename_file(self):
        pass
    
    def view_field_defs(self):
        field_defs = FieldEditor(self)
    
    
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