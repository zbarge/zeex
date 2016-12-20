from core.ctrls.analyze import DataFrameAnalyzer
from core.utility.pandatools import superReadFile
from tests.main import MainTestClass


class TestAnalyzer(MainTestClass):

    def test_model(self, example_file_path):
        df = superReadFile(example_file_path)

        model = DataFrameAnalyzer(df)
        model.process_all_methods()
        assert model.results
        assert 'policyid' in model.results[model.NUMBERS].keys()
        assert 'statecode' in model.results[model.STRINGS].keys()