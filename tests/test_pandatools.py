import pytest
from core.utility.pandatools import *
from tests.main import MainTestClass


class TestClass(MainTestClass):

    def test_super_read_file(self):
        """
        Covering core cases.
        :return:
        """
        df = self.df()
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
                pass

        assert updated_df.index.size == sample_df.index.size + 1, "Should have had 1 additional record appended."

if __name__ == '__main__':
    pytest.main()
