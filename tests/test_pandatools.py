"""
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

import pytest
import shutil
from core.utility.pandatools import *
from tests.main import MainTestClass

SAMPLE_DATE_PASSES = ['2016-10-01', '9/15/2016', '2016-01-01 12:33:45 AM', '09-15-2016', '10-05-88']
SAMPLE_DATE_FAILS = [np.nan, '', '0', 'apples', 1500, 2500]


class TestPandaTools(MainTestClass):

    def test_super_read_file(self, df):
        """
        Covering core cases.
        :return:
        """
        exts = ['.csv','.txt']
        separators = [';',',','|','\t']

        count = 0
        for ext in exts:
            for sep in separators:
                count += 1
                filepath = os.path.join(self.output_dir(), "test_ext{}{}".format(count,ext))
                if os.path.exists(filepath):
                    os.remove(filepath)
                df.to_csv(filepath, sep=sep)
                check_df = superReadFile(filepath, sep=sep)
                assert check_df.index.size == df.index.size, "Extension {} should be supported with sep {}".format(
                                                              ext, sep)
                os.remove(filepath)

    @pytest.mark.parametrize("value", SAMPLE_DATE_PASSES)
    def test_series_to_datetime_pass(self, df, value):
        df.loc[:, 'date_series'] = str(value)
        dtype = str(df.loc[:, 'date_series'].dtype)
        assert dtype == 'object'
        assert series_is_datetime(df.loc[:, 'date_series'])

    @pytest.mark.parametrize("value", SAMPLE_DATE_FAILS)
    def test_series_to_datetime_fail(self, df, value):
        df.loc[:, 'date_series'] = str(value)
        dtype = str(df.loc[:, 'date_series'].dtype)
        assert dtype == 'object'
        assert not series_is_datetime(df.loc[:, 'date_series'])

    @pytest.mark.parametrize("value", SAMPLE_DATE_PASSES)
    def test_dataframe_to_datetime(self, df, value):
        df.loc[:, 'date_series'] = value
        pre_type = str(df['date_series'].dtype)
        df = dataframe_to_datetime(df)
        post_type = str(df['date_series'].dtype)
        assert pre_type == 'object'
        assert post_type == 'datetime64[ns]'

    def test_rename_dupe_cols(self, df):
        df.loc[:, 'NEW_COL'] = ''
        cols = df.columns.tolist()
        cols[-1] = cols[-2]
        assert len(cols) != len(set(cols)), "There should be one duplicate column."

        df.columns = cols
        df.columns = rename_dupe_cols(df.columns)
        cols = df.columns.tolist()

        assert len(cols) == len(set(cols)), "Cols should have been deduplicated."

    def test_set_frame_id(self, df):
        df2 = df.copy()
        orig_size = df.index.size
        df = pd.concat([df, df2])

        # Blank out the id
        df.loc[:, 'id'] = ''

        unique_cols = ['name', 'address']
        id_label = 'id'

        out_df = set_frame_id(df, unique_cols, id_label, start=1)

        out_df.drop_duplicates(['id'], inplace=True)
        assert out_df.index.size == orig_size, "Expected to have the same records as we started with..."

    def test_get_frame_duplicates(self, df):
        df2 = df.copy()
        df.loc[:, 'updated'] = pd.Timestamp('2016-05-05')
        df2.loc[:, 'updated'] = pd.Timestamp('2016-01-01')
        df3 = pd.concat([df, df2])

        id_label = 'id'
        unique_cols = ['address', 'name']
        sort_cols = ['updated']

        df4, df5 = get_frame_duplicates(df3, id_label, unique_cols, sort_cols, ascending=None)

        assert (df4['updated'] == df['updated']).all()
        assert (df5['updated'] == df2['updated']).all()
        assert df4.index.size + df5.index.size == df3.index.size

    @pytest.mark.parametrize('chunksize', list(x for x in range(1, 30, 10)))
    def test_dataframe_chunks(self, example_file_path, chunksize):
        df = superReadFile(example_file_path)
        count, size = 0, 0
        for chunk in dataframe_chunks(df, chunksize=chunksize):
            count += 1
            size += chunk.index.size
        assert count >= int(df.index.size / chunksize)
        assert size == df.index.size

    @pytest.mark.parametrize('chunksize', list(x for x in range(1, 30, 10)))
    def test_dataframe_export_chunks(self, example_file_path, chunksize):
        df = superReadFile(example_file_path)
        check_path = os.path.splitext(example_file_path)[0] + "test_export_dataframe_chunks.csv"
        paths = dataframe_export_chunks(df, check_path, max_size=chunksize)
        return_frame = pd.DataFrame()
        check_base = os.path.splitext(check_path)[0]
        try:
            for p in paths:
                p_base = os.path.splitext(p)[0]
                assert check_base in p_base
            return_frame = pd.concat([superReadFile(p) for p in paths])
        finally:
            [os.remove(p) for p in paths if os.path.exists(p)]

        # Make sure we didnt gain or lose anything.
        assert return_frame.index.size == df.index.size

        # Verify ids of the records.
        for i in range(df.index.size):
            rec = df.iloc[i]
            id = rec['policyid']
            check = return_frame.loc[return_frame['policyid'] == id]
            assert not check.empty

    def test_dataframe_split_to_file(self, example_file_path):
        df = superReadFile(example_file_path)
        dirname = os.path.dirname(example_file_path)
        test_dir = os.path.join(dirname, "split_file_test")
        split_on = 'construction'
        categories = list(df.loc[:, split_on].unique())
        fields = None
        exported_files = None
        return_df = pd.DataFrame()

        try:
            exported_files = dataframe_split_to_files(df, example_file_path, [split_on],
                                                      fields=fields, dropna=False, dest_dirname=test_dir)
            return_frames = [superReadFile(f) for f in exported_files]
            return_df = pd.concat(return_frames)
            assert return_df.index.size == df.index.size
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

        assert exported_files and len(exported_files) == len(categories)
        assert return_df.index.size == df.index.size

        # Verify all policy id's exist both ways
        for idx in return_df.loc[:, 'policyid'].unique():
            match = df.loc[df['policyid'] == idx]
            assert not match.empty

        for idx in df.loc[:, 'policyid'].unique():
            match = return_df.loc[return_df['policyid'] == idx]
            assert not match.empty

    def test_gather_frame_fields(self):
        sample_cols = ['id', 'name', 'address', 'updated']
        sample_recs = [[1000, 'zeke', '123 street'],
                       [1001, 'larry', '688 road'],
                       [1002, 'fred', '585 lane']]

        for rec in sample_recs:
            rec.append(pd.NaT)

        # Copy the original records and make updates.
        update_recs = [rec.copy() for rec in sample_recs]
        for rec in update_recs:
            rec[-1] = pd.Timestamp(datetime.datetime.now()).date()
            rec[-2] = str.title(rec[-2])
            rec[1] = str.title(rec[1])

        # Remove the first record off the sample_recs list
        sample_recs.pop(0)

        # Create our simulated original and updated dataframe.
        sample_df = pd.DataFrame(sample_recs, columns=sample_cols)
        update_df = pd.DataFrame(update_recs, columns=sample_cols)

        # Execute the function
        updated_df = gather_frame_fields(sample_df,
                                         update_df,
                                         index_label='id',
                                         fields=None,
                                         overwrite=True,
                                         copy_frames=True)

        # Iterate through the updated frame and confirm
        # each record has been updated.
        error_count = 0
        for i in updated_df.loc[:, 'id'].tolist():
            try:
                updated_rec = updated_df.loc[updated_df['id'] == i].to_dict(orient='records')[0]
                orig_rec = sample_df.loc[sample_df['id'] == i].to_dict(orient='records')[0]
                update_rec = update_df.loc[update_df['id'] == i].to_dict(orient='records')[0]

                for field in sample_df.columns:
                    if field is not 'id':
                        original = orig_rec[field]
                        update = update_rec[field]
                        updated = updated_rec[field]
                        assert updated != original, "field {} - orig- {}, updated- {}".format(field, original, updated)
                        assert updated == update, "field {} - updated {} - update- {}".format(field, updated, update)
            except IndexError:
                error_count += 1
                # Expecting 1 IndexError here.
                if error_count > 1:
                    raise

        assert updated_df.index.size == sample_df.index.size + 1, "Should have had 1 additional record appended."

if __name__ == '__main__':
    pytest.main()
