import os
import logging
import tkinter as tk
from tkinter import ttk
from dataframe import DataFrameManager
from fieldnames import FieldNames
from compat import string_to_list, string_to_bool
from config import config
from tkinter import messagebox as tkMessageBox
from tkinter import filedialog
from functools import partial
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
        
        entries = self.db.session.query(self.db.Field).order_by(self.db.Field.new_name).all()
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
        
    def build_renames(self):

        filepath = self.master.main_filepath.get()
        source = os.path.basename(filepath)
        df = self.master.framer.read_file(filepath)
        
        order = sorted(df.columns)    
        renames = self.db.get_renames(df.columns)
        nones = [v for v in renames.values() if v is None]
        
        if not nones:
            df.rename(columns=renames, 
                      inplace=True)
            
            if filepath:
                self.master.framer.update_file(filepath, 
                                               df, 
                                               notes="Renamed dataframe.")
                
            tkMessageBox.showinfo("", "File renamed!")
            return None
            
        rename_wdw = tk.Toplevel(self)
        rename_wdw.grid()
        menu = tk.Menu(rename_wdw)
        
        self._current_source = tk.StringVar(rename_wdw, source)
        
        source_label = ttk.Label(rename_wdw, text="Source:")
        source_entry = ttk.Entry(rename_wdw, textvariable=self._current_source)
    
        source_label.grid(row=0, column=0)
        source_entry.grid(row=0, column=1)
        
        row_id = 1
        self._current_entries = []
        
        for old_name in order:
            new_name = renames[old_name]
            
            if new_name is None:
                
                old_label = tk.Label(rename_wdw, text=old_name)
                new_var = tk.StringVar(rename_wdw, old_name)
                new_entry = tk.Entry(rename_wdw, textvariable=new_var)
                self._current_entries.append([old_name, new_var])
                
                old_label.grid(column=0, row=row_id)
                new_entry.grid(column=1, row=row_id)
                row_id += 1
                
        entries_cmd = partial(self._apply_build_renames, 
                              window=rename_wdw)
        
        menu.add_command(label="ADD ENTRIES", command=entries_cmd)
        menu.master.config(menu=menu)
        
    def _apply_build_renames(self, window=None):
        
        source_val = self._current_source.get()
        names = {o:n.get() for o, n in self._current_entries}
        
        entries = self.db.add_entries(names, source=source_val)
        
        [self.insert_entry(e) for e in entries]

        tkMessageBox.showinfo("Complete","Renames applied!")
        
        if window is not None:
            window.destroy()

  
            
            
            
            
class DedupeView(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)

        self.title("Dedupe File")
        self.configure_widgets()
        
    def configure_widgets(self):
        self.columns_box = ttk.Combobox(self)
        
        
class SortView(tk.Toplevel):
    """
    Provides a view to data-sorting options.
    Users can select columns to sort, and also
    the sort order for each column.
    """
    def __init__(self, framer, filepath, master=None):
        tk.Toplevel.__init__(self, master)
        self.filepath = filepath
        self.framer = framer
        self.df = self.framer.read_file(filepath)
        self.title("Sort View")
        self.fields = tk.StringVar(self)
        self.asc = tk.StringVar(self)

        self.configure_widgets()
        
    def configure_widgets(self):
        self.field_label = ttk.Label(self, text="Sort Fields")
        self.left_fbox = tk.Listbox(self, selectmode=tk.EXTENDED)
        [self.left_fbox.insert(tk.END, c) for c in self.df.columns]
        self.right_fbox = tk.Listbox(self, selectmode=tk.EXTENDED, listvariable=self.fields)
        
        self.asc_label = ttk.Label(self, text="Sort Ascending")
        self.left_abox = tk.Listbox(self, selectmode=tk.EXTENDED)
        [self.left_abox.insert(tk.END, c) for c in ['True', 'False']]
        self.right_abox = tk.Listbox(self, selectmode=tk.EXTENDED, listvariable=self.asc)
        
        self.execute_btn = ttk.Button(self, text="Execute", command=self.execute_sort)
        self.reset_btn = ttk.Button(self, text="Reset", command=self.reset_sort)
        
        fbox_push_cmd = partial(self.push_right, 
                                self.left_fbox, 
                                self.right_fbox,
                                remove=True)
        self.push_fbox_right_btn = ttk.Button(self, text="-->", command=fbox_push_cmd)
        
        abox_push_cmd = partial(self.push_right, 
                                self.left_abox, 
                                self.right_abox,
                                remove=False)
        self.push_abox_right_btn = ttk.Button(self, text="-->", command=abox_push_cmd)        
        
        self.field_label.grid(row=0, column=0)
        self.reset_btn.grid(row=0, column=1)
        self.left_fbox.grid(row=1, column=0)
        self.push_fbox_right_btn.grid(row=1, column=1)
        self.right_fbox.grid(row=1, column=2)
        
        self.asc_label.grid(row=2, column=0)
        
        self.left_abox.grid(row=3, column=0)
        self.push_abox_right_btn.grid(row=3, column=2)
        self.right_abox.grid(row=3, column=2)
        
        self.execute_btn.grid(row=4, column=0)
        
    def push_right(self, leftbox, rightbox, remove=True):
        idxs = map(int, leftbox.curselection())
        
        for i in idxs: 
            value = leftbox.get(i)
            rightbox.insert('end', value)
            
        if remove:
            [leftbox.delete(i) for i in idxs]
            
    def reset_sort(self):
        self.right_fbox.select_set(0, tk.END)
        self.right_abox.select_set(0, tk.END)
        
        for i in map(int, self.right_fbox.curselection()):
            self.left_fbox.insert(tk.END, self.right_fbox.get(i))
            self.right_fbox.delete(i)
            
        for i in map(int, self.right_abox.curselection()):
            self.left_abox.insert(tk.END, self.right_abox.get(i))
            self.right_abox.delete(i)
            
    def execute_sort(self):
        self.right_fbox.select_set(0, tk.END)
        
        
        on = [self.right_fbox.get(i) 
              for i in map(int, self.right_fbox.curselection())]
              
        self.right_abox.select_set(0, tk.END)      
        ascending = [string_to_bool(self.right_abox.get(i)) 
                     for i in map(int,self.right_abox.curselection() )]
                     
        if not on or not ascending:
            msg = "choose a sort order and ascending order. Parameters:{}".format(
                         [on, ascending])
            tkMessageBox.showerror("Sort Attention Required", msg)
            raise KeyError(msg)
            
        try:
            self.df.sort_values(on, ascending=ascending, inplace=True)
            
        except (KeyError, IndexError) as e:
            msg = "Error: '{}'\n\nColumns available: {}\n\nParameters: {}".format(
                   e, self.df.columns, [on, ascending])
            logger.warning(msg)
            tkMessageBox.showerror(title="Sort Error", message=msg)
            raise KeyError(msg)
            
        notes = "Sorted data: on='{}', ascending='{}'".format(on, ascending)    
        logger.info(notes)    
        self.framer.update_file(self.filepath, self.df, notes=notes)
        tkMessageBox.showinfo("Sort Complete", notes)
        self.master.focus_set()
        
        
        
class FileView(tk.Toplevel):
    def __init__(self, filepath, framer, master=None):
        tk.Toplevel.__init__(self, master)
        self.title(filepath)
        self.grid()
        self.minsize(width=666, height=666)
        self.config(padx=10, pady=10)
        self.framer = framer
        self.filepath = filepath
        self.df = self.framer.read_file(filepath)
        self.cur_idx = 0
        self._page_size = 150
        
        self.configure_widgets()
        
    @property
    def columns(self):
        return self.df.columns
        
    @property
    def index(self):
        return self.df.index
        
    @property
    def size(self):
        return self.index.size
    @property
    def page_size(self):
        return self._page_size
        
    @page_size.setter
    def page_size(self, x):
        assert x < 200, "FileView.page_size can be no more than {}, not {}.".format(200, x)
        self._page_size = x
        
    def configure_widgets(self):
        self.menu = tk.Menu(self)
        self.menu.add_command(label="Save", command=self.save_file)
        self.menu.add_command(label="Save As", command=partial(self.save_file, save_as=True))
        self.menu.add_command(label="Refresh", command=self.refresh_tree)
        self.menu.add_command(label="Page Left", command=self.page_left)
        self.menu.add_command(label="Page Right", command=self.page_right)
        action_menu = tk.Menu(self)
        
        action_menu.add_command(label="Dedupe", command=self.dedupe_file)
        action_menu.add_command(label="Sort", command=self.sort_file)
        action_menu.add_command(label="Suppress", command=self.suppress_file)
        action_menu.add_command(label="Merge", command=self.merge_file)
        action_menu.add_command(label="Split", command=self.split_file)
        action_menu.add_command(label="Update", command=self.update_file)
        action_menu.add_command(label="Rename", command=self.rename_file)
        self.menu.add_cascade(label="Actions", menu=action_menu)
        self.config(menu=self.menu)
        self.configure_tree()
        self.insert_records(self.cur_idx, self.page_size, replace=True)
        
    def dedupe_file(self):
        pass
    
    def sort_file(self):
        return SortView(self.framer, self.filepath, self)
    
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
    
    def save_file(self, save_as=False):
        from_path = self.filepath
        if not from_path:
            return
            
        if save_as is True:
            save_as = filedialog.asksaveasfilename(initialfile=from_path)
            
        if save_as:
           to_path = save_as
           info = "Saved file: {} as {}".format(from_path, to_path)
        else:
            to_path = from_path
            info = "Saved file: {}".format(to_path)
            
        self.framer.save_file(from_path, save_as=save_as)
        logger.info(info)
        tkMessageBox.showinfo("File Saved: {}".format(to_path))
        self.focus_set()
        
    def page_left(self):
        if self.cur_idx < self.page_size:
            return None
        else:
            self.cur_idx -= self.page_size
            max_idx = self.cur_idx + self.page_size + 1
            self.insert_records(self.cur_idx, max_idx, replace=True)
            
    def page_right(self):
        if self.cur_idx >= self.size:
            return None
        else:
            self.cur_idx += self.page_size
            max_idx = self.cur_idx + self.page_size + 1
            self.insert_records(self.cur_idx, max_idx, replace=True)
            
    def configure_tree(self):
        """
        Configures TreeView based on dataframe
        stored in FileView.df
        """
        if hasattr(self, "tree"):
            return None

        cols = list(self.columns)
        iname = ("idx" if self.index.name is None else self.index.name)
        cols.insert(0, iname)
        self.tree = ttk.Treeview(self, columns=cols, height=50)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        
        for i, c in enumerate(cols):
            title = "#" + str(i)
            self.tree.heading(title, text=c)
            self.tree.column(i, width=100)
        self.tree.grid(row=0, column=0, columnspan=len(cols))
        
        ysb.grid(row=0,
                 column=1,
                 sticky='ns',
                 in_=self)
        xsb.grid(row=0, 
                 column=0,
                 columnspan=len(cols),
                 sticky='ew',
                 in_=self)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
    def refresh_tree(self):
        self.cur_idx = 0
        self.insert_records(self.cur_idx, self.page_size, replace=True) 
        
    def insert_records(self, from_idx, to_idx, replace=True):
        """
        Loads dataframe records into the FileView.tree
        from_idx: (int) - the start index
        to_idx: (int) - the to index
        replace: (bool) - Default True removes current children in the tree
        """
        
        if replace:
            kids = self.tree.get_children()
            if kids:
                self.tree.delete(*kids)
                        
        idxs = [x for x in range(from_idx, to_idx) if not self.tree.exists(x)]
        
        for rec_idx in idxs:
            rec = self.df.iloc[rec_idx]
            values = [rec[c] for c in self.columns]
            self.tree.insert("", "end", rec_idx, text=rec_idx, values=values)        


class MainView(ttk.Frame):
    
    def __init__(self, master=None):

        master.title("DBTrix")
        master.minsize(width=666, height=666)
        master.maxsize(width=666, height=666)            
        ttk.Frame.__init__(self, master)
        self.main_filepath = tk.StringVar(self)
        self.framer = DataFrameManager()
        self.grid()
        self.create_widgets()
        self._file_views = {}
        
    def create_widgets(self):
        
        self.main_menu = tk.Menu(self)
        
        file_menu = tk.Menu(self.main_menu)
        file_menu.add_command(label="Open", command=self.open_fileview)
        file_menu.add_command(label="Drop", command=self.drop_file)
        
        self.main_menu.add_cascade(label="File", menu=file_menu)
        self.main_menu.add_command(label="Field Names", command=self.view_field_defs)
        self.master.config(menu=self.main_menu)
        
        self.main_file_label = ttk.Label(self, text="Working File:")
        self.main_file_entry =  ttk.Entry(self, textvariable=self.main_filepath)

        self.main_file_label.grid(row=1, column=0)
        self.main_file_entry.grid(row=1, column=2)
        
    def drop_file(self):
        fp = self.main_filepath.get()
        self.main_filepath.set("")
        self.framer.remove_file(fp)
        logger.info("Removed file: {}".format(fp))
        
    def save_file(self, save_as=False):
        from_path = self.main_filepath.get()
        if not from_path:
            return
            
        if save_as is True:
            save_as = filedialog.asksaveasfilename(initialfile=from_path)
            
        if save_as:
           to_path = save_as
           info = "Saved file: {} as {}".format(from_path, to_path)
        else:
            to_path = from_path
            info = "Saved file: {}".format(to_path)
            
        self.framer.save_file(from_path, save_as=save_as)
        logger.info(info)
        tkMessageBox.showinfo("File Saved: {}".format(to_path))
        self.focus_set()
        

    def view_field_defs(self):
        return FieldEditor(self)
        
    def open_fileview(self):
        fp = self.main_filepath.get()
        
        if not fp:
            fp = filedialog.askopenfilename()
            self.main_filepath.set(fp)
            
        fv = FileView(fp, self.framer, self)
        self.wait_window(self)
        return fv
            

    
def main():
    root = tk.Tk()
    try:
        app = MainView(root)
        app.mainloop()
    finally:
        try:
            root.destroy()
        except:
            pass
    

if __name__ == "__main__":
    main()