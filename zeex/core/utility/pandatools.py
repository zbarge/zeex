# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 00:03:14 2016

@author: Zeke
"""

import os
import datetime
import pandas as pd


def force_int(integer):
    integer = ''.join(e for e in str(integer) if e.isdigit() or e is '.')
    try:
        return int(integer)
    except:
        return 0


def superReadCSV(filepath, first_codec='utf8', usecols=None, 
                 low_memory=False, dtype=None, parse_dates=True, 
                 sep=',', chunksize=None, verbose=False, **kwargs):
        """ A wrap to pandas read_csv with mods to accept a dataframe or filepath. returns dataframe untouched, reads filepath and returns dataframe based on arguments."""
        if isinstance(filepath, pd.DataFrame): return filepath
        assert isinstance(first_codec, str), "first_codec parameter must be a string"
        
        codecs = list(set([first_codec] + ['utf8','iso-8859-1','ascii','utf-16','utf-32']))
        
        for c in codecs:
            try:
                
                return pd.read_csv(filepath,usecols=usecols,low_memory=low_memory,encoding=c,dtype=dtype,parse_dates=parse_dates,sep=sep,chunksize=chunksize,**kwargs)
            
            except (UnicodeDecodeError, UnboundLocalError) as e:
                if verbose: 
                    print(e)
            except Exception as e:
                if 'tokenizing' in str(e):
                    pass
                else:
                    raise
        raise Exception("Tried {} codecs and failed on all: \n CODECS: {} \n FILENAME: {}".format(
                        len(codecs), codecs, os.path.basename(filepath)) )
        
def _count(item,string):
    if len(item) == 1:
        return len(''.join(x for x in string if x == item))
    return len(str(string.split(item)))
    
def identify_sep(filepath):
    """Identifies the separator of data in a filepath.
    It reads the first line of the file and counts supported separators.
    Currently supported separators: ['|', ';', ',','\t',':']"""
    ext = os.path.splitext(filepath)[1].lower()
    allowed_exts = ['.csv', '.txt', '.tsv']
    assert ext in ['.csv', '.txt'], "Unexpected file extension {}. \
                                    Supported extensions {}\n filename: {}".format(
                                    ext, allowed_exts, os.path.basename(filepath))
    maybe_seps = ['|',
                  ';',
                  ',',
                  '\t',
                  ':']
                  
    with open(filepath,'r') as fp:
        header = fp.__next__()
        
    count_seps_header = {sep:_count(sep,header) for sep in maybe_seps}
    count_seps_header = {sep:count for sep,count in count_seps_header.items() if count > 0}
    
    if count_seps_header:
        return max(count_seps_header.__iter__(), 
                   key=(lambda key: count_seps_header[key]))
    else:
        raise Exception("Couldn't identify the sep from the header... here's the information:\n HEADER: {}\n SEPS SEARCHED: {}".format(header,maybe_seps))

def superReadText(filepath,**kwargs):
    """ 
    A wrapper to superReadCSV which wraps pandas.read_csv().
    The benefit of using this function is that it automatically identifies the column separator.
    .tsv files are assumed to have a \t (tab) separation
    .csv files are assumed to have a comma separation.
    .txt (or any other type) get the first line of the file opened 
        and get tested for various separators as defined in the identify_sep function.   
    """
    if isinstance(filepath,pd.DataFrame): 
        return filepath
    sep = kwargs.get('sep',None)
    ext = os.path.splitext(filepath)[1].lower()
    
    if sep is None:
        if ext == '.tsv':
            kwargs['sep'] = '\t'
            
        elif ext == '.csv':
            kwargs['sep'] = ','
            
        else:
            found_sep = identify_sep(filepath)
            print(found_sep)
            kwargs['sep'] = found_sep
            
    return superReadCSV(filepath,**kwargs)

def superReadFile(filepath,**kwargs):
    """ 
    Uses pandas.read_excel (on excel files) and returns a dataframe of the first sheet (unless sheet is specified in kwargs)
    Uses superReadText (on .txt,.tsv, or .csv files) and returns a dataframe of the data.
    One function to read almost all types of data files.    
    """
    if isinstance(filepath,pd.DataFrame): return filepath
        
    excels = ['.xlsx','.xls']
    texts = ['.txt','.tsv','.csv']
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext in excels:
        return pd.read_excel(filepath,**kwargs)
    elif ext in texts:
        return superReadText(filepath,**kwargs)
    else:
        raise Exception("Unsupported filetype: {}\n Supported filetypes: {}".format(ext,excels + texts))
    
  
def dedupe_cols(frame):
    """
    Need to dedupe columns that have the same name.
    """
    cols = list(frame.columns)
    for i, item in enumerate(frame.columns):
        if item in frame.columns[:i]: 
            cols[i] = "toDROP"
    frame.columns = cols
    return frame.drop("toDROP", 1, errors='ignore')

def rename_dupe_cols(cols):
    """Takes a list of strings and appends 2,3,4 etc to duplicates. Never appends a 0 or 1. 
    Appended #s are not always in order...but if you wrap this in a dataframe.to_sql function you're guaranteed
    to not have dupe column name errors importing data to SQL...you'll just have to check yourself to see which fields were renamed."""
    counts = {}
    positions = {pos: fld for pos, fld in enumerate(cols)}
    
    for c in cols:
        if c in counts.keys():
            counts[c] +=1
        else:
            counts[c] = 1
            
    fixed_cols = {}
    
    for pos,col in positions.items():
        if counts[col] > 1:
            fix_cols = {pos: fld for pos,fld in positions.items() if fld == col}
            keys = [p for p in fix_cols.keys()]
            min_pos = min(keys)
            cnt = 1
            for p,c in fix_cols.items():
                if not p == min_pos:
                    cnt += 1
                    c = c + str(cnt)
                    fixed_cols.update({p:c})
                    
    positions.update(fixed_cols)
    
    cols = [x for x in positions.values()]
    
    return cols


def set_frame_id(df, unique_cols, id_label, start=1):
    """
    Assigns a numeric id to a dataframe based on unique columns.

    df (DataFrame) the dataframe to assign the id to.
    unique_cols (list) the list of columns that must be unique.
    id_label (str) the name of the id column to add.
    start (int) the start id of the new DataFrame
                This is overridden to the max_id + 1 if
                the *arg::id_label already exists.

    Returns: A DataFrame with a unique numeric key named id_label
    """

    df = df.copy()
    key_cols = unique_cols.copy()

    orig_order = df.columns.tolist()

    if id_label not in df.columns:
        # We want the id_label to be added
        # to the end of the column order.
        orig_order.append(id_label)

    elif id_label not in unique_cols:
        # We want to take the id
        # and preserve it with the unique records.
        unique_cols.append(id_label)

    # Split off unique columns to a frame/dedupe
    df_unique = df.loc[:, unique_cols]
    df_unique.drop_duplicates(subset=key_cols, inplace=True)

    if id_label in df_unique.columns:
        # find out if records are missing an id.
        # Coerce the id_label into numeric digits.
        df_unique.loc[:, id_label] = df_unique.loc[:, id_label].apply(force_int).astype(int)

        # Drop NaNs and take all > 0
        id_mask = df_unique[id_label] > 0
        has_ids = df_unique.loc[id_mask, id_label].dropna()

        # Now we can count missing IDs
        count_missing = df_unique.index.size - has_ids.index.size

        if count_missing > 0:
            # yes records are missing an id.
            # Get the max id and add 1 to it for our start.
            start = df_unique.loc[:, id_label].max() + 1
            new_ids = list(range(start, count_missing + start))

            # Get the positions that need updating.
            fill_mask = [x for x in df_unique.index
                         if x not in has_ids.index]

            # Assign the new ids to the positions.
            df_unique.loc[fill_mask, id_label] = new_ids

    else:
        # We just need to create a new range from start to size.
        df_unique.loc[:, id_label] = list(range(start, df_unique.index.size + start))

    # Get rid of the ID on the original dataframe if it exists.
    df = df.drop([id_label], axis=1, errors='ignore')

    # Guarantee that all records have unique ids:
    guarantee = len(df_unique.loc[:, id_label].unique()) == df_unique.index.size
    assert guarantee, "Not all record IDs were unique - we failed somehow. Investigate."

    # Return a new dataframe of the records
    # merged together on the unique_key columns.
    # Formats to the original dataframe
    # column order (+ id_label if it didnt exist).
    return pd.merge(df_unique, df,
                 left_on=key_cols,
                 right_on=key_cols,
                 how='left').loc[:, orig_order]


def get_frame_duplicates(df, id_label, unique_cols, sort_cols, ascending=None):
    """
    deduplicates a dataframe based on unique columns passed
    to the col_lists argument. All returned records will have
    a unique numeric key in the column named in the id_label argument.

    df (DataFrame)
        The DataFrame to split
    id_label (str)
        name of the column with ids (doesnt have to exist)
    unique_cols (list)
        of column names that make each record unique
    sort_cols (list)
        of columns to sort by (a date, perhaps?)
    ascending (list)
        with a boolean for each column in sort_columns indicating whether the column should
        be sorted ascending or descending BEFORE unique id's are assigned.
        The data will be sorted in the exact opposite order before it is deduplicated.

    Returns a list like [df, dupe_df]

    Example:
    ----------------------------------------------------

    df, dupedf = split_frame_dupes(df,
                                   'record_id',
                                   ['name', 'address'],
                                   ['insert_date'])
    """

    if ascending is not None:
        pre_asc = ascending.copy()
        post_asc = [(True if b is False else False) for b in pre_asc]
    else:
        pre_asc = [True for b in sort_cols]
        post_asc = [False for b in sort_cols]


    # Do the pre-sort
    df.sort_values(sort_cols, ascending=pre_asc, inplace=True)

    # Apply the ID assignment algo
    df = set_frame_id(df, unique_cols, id_label)

    # Do the post-sort and dedupe.
    df.sort_values(sort_cols, ascending=post_asc, inplace=True)
    df_deduped = df.drop_duplicates(subset=unique_cols)

    # Get index ids of records that were deduped (in)
    in_mask = [x for x in df.index if x not in df_deduped.index]
    # versus not deduped (out)
    out_mask = [x for x in df.index if x not in in_mask]

    # Store records that died
    dupe_df = df.loc[in_mask, :]

    # Replace the df with out_mask records.
    df = df.loc[out_mask, :]

    return [df, dupe_df]


def gather_frame_fields(df: pd.DataFrame, other_df: pd.DataFrame, index_label: str=None,
                        fields: list=None, copy_frames: bool=False,
                        append_missing: bool=True, **kwargs):

    if copy_frames:
        df = df.copy()
        other_df = other_df.copy()

    if index_label is not None:
        for frame in [df, other_df]:
            if frame.index.name is not index_label and index_label in frame.columns:
                frame.set_index(index_label, drop=False, inplace=True)

    if fields:
        other_df_orig = other_df.copy()
        other_df = other_df.loc[:, fields]
    else:
        other_df_orig = other_df

    df.update(other_df, **kwargs)

    if append_missing is True:
        df_add = other_df_orig.loc[~other_df_orig.index.isin(df.index), :]
        df = pd.concat([df, df_add])

    return df















