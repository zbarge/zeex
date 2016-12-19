# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 00:03:14 2016
MIT License

Copyright (c) 2016 Zeke Barge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import datetime
import pandas as pd
import numpy as np
from core.utility.ostools import path_incremented

def force_int(integer):
    integer = ''.join(e for e in str(integer) if e.isdigit() or e is '.')
    try:
        return int(integer)
    except:
        return 0


def dataframe_chunks(df, chunksize=None):
    """
    Yields chunks from a dataframe as large as chunksize until
    there are no records left.

    :param df: (pd.DataFrame)
    :param chunksize: (int, default None)
        The max rows for each chunk.
    :return: (pd.DataFrame)
        Portions of the dataframe
    """
    if chunksize is None or chunksize <= 0 or chunksize >= df.index.size:
        yield df
    else:
        while df.index.size > 0:
            take = df.iloc[0:chunksize]
            #df = df.loc[~df.index.isin(take.index), :]
            df = df.iloc[chunksize:df.index.size]
            yield take


def dataframe_export(df, filepath, **kwargs):
    """
    A simple dataframe-export either to csv or excel.

    :param df: (pd.DataFrame)
        The dataframe to export
    :param filepath: (str)
        The filepath to export to.

    :param kwargs: (pd.to_csv/pd.to_excel kwargs)
        Look at pandas documentation for kwargs.
    :return: None
    """
    filebase, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext is '.xlsx':
        df.to_excel(filepath, **kwargs)
    elif ext in ['.txt','.csv']:
        df.to_csv(filepath, **kwargs)
    else:
        raise NotImplementedError("Not sure how to export '{}' files.".format(ext))


def dataframe_export_chunks(df, filepath, max_size=None, overwrite=True, **kwargs):
    """
    Exports a dataframe into chunks and returns the filepaths.

    :param df: (pd.DataFrame)
        The DataFrame to export in chunks.
    :param filepath: (str)
        The base filepath (will be incremented by 1 for each export)
    :param max_size: (int, default None)
        The max size of each dataframe to export.
    :param kwargs: (pd.to_csv/pd.to_excel kwargs)
        Look at pandas documentation for kwargs.
    :return: list(filepaths exported)
    """
    paths = []
    for chunk in dataframe_chunks(df, chunksize=max_size):
        dataframe_export(chunk, filepath, **kwargs)
        paths.append(filepath)
        filepath = path_incremented(filepath, overwrite=overwrite)

    return paths


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
            kwargs['sep'] = found_sep
            
    return superReadCSV(filepath,**kwargs)


def superReadFile(filepath,**kwargs):
    """ 
    Uses pandas.read_excel (on excel files) and returns a dataframe of the first sheet (unless sheet is specified in kwargs)
    Uses superReadText (on .txt,.tsv, or .csv files) and returns a dataframe of the data.
    One function to read almost all types of data files.    
    """
    if isinstance(filepath, pd.DataFrame):
        return filepath

    ext = os.path.splitext(filepath)[1].lower()
    
    if ext in ['.xlsx', '.xls']:
        return pd.read_excel(filepath,**kwargs)

    elif ext in ['.txt','.tsv','.csv']:
        return superReadText(filepath,**kwargs)

    else:
        raise NotImplementedError("Unable to read '{}' files".format(ext))
    
  
def dedupe_cols(df):
    """
    Removes duplicate columns from a dataframe.
    Only the first occurrence of each column label
    is kept.
    """
    tag = "REMOVE_ME_PLEASE"
    cols = list(df.columns)
    for i, item in enumerate(df.columns):
        if item in df.columns[:i]:
            cols[i] = tag
        df.columns = cols
    return df.drop(tag, 1, errors='ignore')


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
    
    for pos, col in positions.items():
        if counts[col] > 1:
            fix_cols = {pos: fld for pos,fld in positions.items() if fld == col}
            keys = [p for p in fix_cols.keys()]
            min_pos = min(keys)
            cnt = 1
            for p, c in fix_cols.items():
                if not p == min_pos:
                    cnt += 1
                    c = c + str(cnt)
                    fixed_cols.update({p: c})
                    
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
    """
    Updates a dataframe from another based on common index (or index_label) keys.

    :param df: (pd.DataFrame)
        The master dataframe to be updated
    :param other_df: (pd.DataFrame)
        The other dataframe to gather data from
    :param index_label: (str, default None)
        The name of the index column
        This column will be set to the index of the dataFrame if it's not already.
        If the index has no name, and the index_label is not in the frame's columns
        The current index's name will be set to index_label.
    :param fields: (list, default None)
        An optional subset of field names to gather data from rather than updating from all
        fields in the :param other_df.
    :param copy_frames: (bool, default False)
        True creates a copy of the data before doing any operations (safer?)
    :param append_missing: (bool, default True)
        True appends records to :param df from :param other_df with an index did not exist in :param df.
    :param kwargs: pd.DataFrame.update(**kwargs)

    :return: (pd.DataFrame)
        :param df that has updated data from :param other_df
    """
    if copy_frames:
        df = df.copy()
        other_df = other_df.copy()

    if index_label is not None:
        for frame in [df, other_df]:
            if frame.index.name is not index_label and index_label in frame.columns:
                frame.set_index(index_label, drop=False, inplace=True)
            else:
                frame.index.name = index_label

    if fields:
        other_df_orig = other_df.copy()
        if isinstance(fields, str):
            fields = [fields]
        elif not hasattr(fields, '__iter__'):
            raise Exception("Fields must be iterable or a string.. not {}".format(type(fields)))
        elif not isinstance(fields, list):
            fields = list(fields)
        other_df = other_df.loc[:, fields]
    else:
        other_df_orig = other_df

    df.update(other_df, **kwargs)

    if append_missing is True:
        df_add = other_df_orig.loc[~other_df_orig.index.isin(df.index), :]
        df = pd.concat([df, df_add])

    return df


def series_is_datetime(series: pd.Series, check_num: int=5, dropna: bool=True):
    """
    Checks random rows in a Series comparing rows that coerce to datetime.
    :param series:
    :param check_num:
    :param dropna:
    :return:
    """
    if dropna:
        series = series.dropna(axis=0)
    got, lost = 0, 0
    size = (check_num if series.index.size > check_num else series.index.size)

    if size > 0:
        checks = np.random.randint(0, high=series.index.size, size=size)
        for x in series[checks].tolist():
            try:
                x = pd.Timestamp(x)
                if pd.notnull(x):
                    got += 1
            except (ValueError, OverflowError):
                lost += 1

    return got > lost


def series_to_datetime(series, check_num: int=5, dropna: bool=True, **kwargs):
    """

    :param series: (pd.Series)
        The series object to modify.
    :param check_num: (int, default 10)
        The max number of rows to test for coerceable datetime values.
    :param dropna: (bool, default True)
        True drops na values from the series before checking random rows.
    :param kwargs: pd.to_datetime(**kwargs)
        errors: defaults to 'coerce'
    :return: (pd.Series)
        With dtype converted to a datetime if possible.
    """
    if series_is_datetime(series, check_num=check_num, dropna=dropna):
        kwargs['errors'] = kwargs.get('errors', 'coerce')
        series = pd.to_datetime(series, **kwargs)
    return series


def dataframe_to_datetime(df, dtypes=['object'], check_num:int = 5, dropna: bool=True, raise_on_error=False, **kwargs):
    """
    Scans columns in a dataframe looking for columns to convert into a DateTime.

    :param df: (pd.DataFrame)
        The dataframe to modify.
    :param dtypes: (list, default ['object'])
        A list of data types to check.
    :param check_num: (int, default 10)
        The max number of rows to test for coerceable datetime values.
    :param dropna: (bool, default True)
        True drops na values from the series before checking random rows.
    :param raise_on_error: (bool, default False)
        True raises ValueError or OverflowError if any occur doing the conversion.
    :param kwargs: pd.to_datetime(**kwargs)
        errors: defaults to 'coerce'
    :return: (pd.DataFrame)
        DataFrame with found datetime columns converted.
    """
    for column in df.columns:
        dtype = str(df[column].dtype)
        if dtype in dtypes:
            try:
                converted = series_to_datetime(df.loc[:, column], check_num=check_num, dropna=dropna, **kwargs)
                df.loc[:, column] = converted
            except (ValueError, OverflowError):
                if raise_on_error:
                    raise
    return df


def dataframe_split_to_files(df: pd.DataFrame, source_path: str, split_on: list,
                             fields: list=None, dropna: bool=False, dest_dirname:str =None,
                             chunksize: int=None, **kwargs):
    """
    Somewhat intelligently splits and exports a DataFrame into separate files based on the given parameters.

    :param df: (pd.DataFrame)
        The dataframe to split
    :param source_path: (str)
        A filepath to use as the base filename/extension for exports
        (and directory name if dest_dirname is None)
    :param split_on: (list)
        The list of column(s) to split the dataframe on.
        Each value in a split_on column will be paired with a value from
        the other column(s) (if any) and will
    :param fields: (list, default None)
        A subset of fields to export in each split.
        If None, all fields will be exported.
    :param dropna: (bool, default False)
        NA values are either dropped or filled with the word 'blank'
        which will show up in the filename.
    :param dest_dirname: (str, default None)
        A destination directory to store the splits.
        If None is specified, the source_path's directory will be used.
    :param chunksize: (int, default None)
        The max # of records to export per file.
    :return: list(exported filepaths)
    """
    source_base, source_ext = os.path.splitext(os.path.basename(source_path))
    if dest_dirname is not None:
        dirname = dest_dirname
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    else:
        dirname = os.path.dirname(source_path)

    if not fields:
        fields = df.columns.tolist()

    if dropna:
        if not split_on:
            subset = None
        else:
            subset = split_on
        df.dropna(how='any', subset=subset, inplace=True)
    elif split_on:
        [df.loc[:, c].fillna('blank', inplace=True) for c in split_on]

    if not split_on:
        df = df.loc[:, fields]
        file_path = os.path.join(dirname, source_base + source_ext)
        exported_paths = dataframe_export_chunks(df, file_path, max_size=chunksize, **kwargs)

    else:

        combos = {c: list(df.loc[:, c].unique()) for c in split_on}
        keys, exported_paths = [], []

        # TODO: This feels like it should be some sort of recursive function...
        # Learn this shit and make it split better using all available options
        # From the combos.
        for col, values in combos.items():
            other_cols = [c for c in combos.keys() if c != col]
            if other_cols:
                for val in values:
                    for other_col in other_cols:

                        other_vals = combos[other_col]
                        for other_val in other_vals:

                            key = ''.join(list(sorted([str(val), str(other_val)])))
                            if key not in keys:

                                mask = ((df.loc[:, col] == val) & (df.loc[:, other_col] == other_val))
                                df_part = df.loc[mask, fields]
                                if not df_part.empty:

                                    name_str = "{}_{}_{}_{}".format(str(col)[:5], val, str(other_col)[:5], other_val)
                                    name_str = ''.join(e for e in str(name_str)
                                                       if e.isalnum() or e == '_').strip().lower()
                                    name_str = "{}_{}{}".format(source_base, name_str, source_ext)
                                    out_path = os.path.join(dirname, name_str)

                                    paths = dataframe_export_chunks(df_part, out_path, max_size=chunksize, **kwargs)
                                    keys.append(key)
                                    exported_paths.extend(paths)
            else:
                for val in values:

                    df_part = df.loc[df[col] == val, fields]
                    if not df_part.empty:

                        val = ''.join(e for e in str(val) if e.isalnum() or e == '_').strip().lower()
                        name_str = "{}_{}{}".format(source_base, val, source_ext)
                        out_path = os.path.join(dirname, name_str)

                        paths = dataframe_export_chunks(df_part, out_path, max_size=chunksize, **kwargs)
                        exported_paths.extend(paths)

    return exported_paths











