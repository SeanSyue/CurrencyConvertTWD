import configparser
import shutil
from unittest import TestCase
from pathlib import Path
from contextlib import contextmanager

from currency_converter_twd.TableManager import TableCaches
from currency_converter_twd.TableManager import FileSystemManager

config = configparser.ConfigParser()
config.read('currency_converter_twd/config.ini')

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']


class TestTableCaches(TestCase):

    def setUp(self) -> None:
        self.__table_caches = TableCaches()

    def test_if_set_outdated_tables_as_non_set(self):
        with self.assertRaises(TypeError):
            self.__table_caches.outdated_tables = 'a'

    def test_if_set_active_tables_as_non_str(self):
        with self.assertRaises(TypeError):
            self.__table_caches.outdated_tables = 0

    def test_setting_active_table_with_outdated_table_exists(self):
        self.__table_caches.outdated_tables = {'existed_1', 'existed_2'}
        self.__table_caches.active_table = 'new_1'
        # set a new `active_table`
        self.__table_caches.active_table = 'new_2'

        # Check if `active_table` set correctly
        self.assertEqual(self.__table_caches.active_table, 'new_2')
        # Check if `outdated_tables` caches previous `active_table`
        self.assertEqual(self.__table_caches.outdated_tables, {'existed_1', 'existed_2', 'new_1'})


class TestFileSystemManagerParent(TestCase):
    @contextmanager
    def _mock_tables_test(self, folder_, *tables_, mkdir_=True):
        """
        wrapper for setup and teardown
        determine whether makes mocked folder or mocked tables individually
        set "file system manager" instance for testing
        remove folder generated during tearing down
        @param folder_: mocked folder
        @param tables_: mocked tables
        @param mkdir_: whether makes mocked folder
        """
        try:
            # TODO: log file making
            if mkdir_:  # make mock table folder
                folder_.mkdir(exist_ok=True)
                if tables_:  # generate mock tables
                    for file in tables_:
                        folder_.joinpath(file).touch()
            self.__sys_mgr = FileSystemManager(folder_)
            yield
        finally:
            # TODO: log file deleting
            shutil.rmtree(folder_)

    def _do_delete_testing(self, folder_, expected_active_table_):
        """
        do delete outdated tables
        check if table cache is set properly
        check if intended files are cleaned and active table exists
        @param folder_: mocked folder
        @param expected_active_table_: expected value for active table
        """
        self.__sys_mgr.delete_outdated_tables()
        # check if table cache is set properly
        self.assertEqual(self.__sys_mgr.active_table, expected_active_table_)
        self.assertEqual(len(self.__sys_mgr.outdated_tables), 0)

        # check if only expected active table remain in the folder
        indices = list(Path(folder_).glob('*.csv'))
        remaining_tables = [n.name for n in Path(folder_).glob('*.csv')] if indices else ['']
        self.assertEqual(len(remaining_tables), 1)
        self.assertEqual(remaining_tables[0], expected_active_table_)

    def __init__(self, context_, *args, **kwargs):
        """
        create text context for testing
        @param context_: context for different test case
        """
        super().__init__(*args, **kwargs)
        self.__test_context = context_

    # Ref:
    # https://stackoverflow.com/questions/25233619/testing-methods-each-with-a-different-setup-teardown/25234865#25234865
    def setUp(self) -> None:
        self.__test_context.__enter__()

    def tearDown(self) -> None:
        self.__test_context.__exit__(None, None, None)


class TestFileSystemManagerWithExistingTables(TestFileSystemManagerParent):
    __mock_table_folder = Path(__file__).parent.joinpath('test-' + _FOLDER)
    __mock_tables = [f'ExchangeRate@201912021{i}00.csv' for i in range(3, 6)]

    def __init__(self, *args, **kwargs):
        self.__test_context = self._mock_tables_test(self.__mock_table_folder, *self.__mock_tables)
        super().__init__(self.__test_context, *args, **kwargs)

    def test_delete_outdated_tables(self):
        self._do_delete_testing(self.__mock_table_folder, max(self.__mock_tables))


class TestFileSystemManagerWithEmptyFolder(TestFileSystemManagerParent):
    __mock_empty_table_folder = Path(__file__).parent.joinpath('empty-' + _FOLDER)

    def __init__(self, *args, **kwargs):
        self.__test_context = self._mock_tables_test(self.__mock_empty_table_folder)
        super().__init__(self.__test_context, *args, **kwargs)

    def test_delete_outdated_tables(self):
        self._do_delete_testing(self.__mock_empty_table_folder, '')


class TestFileSystemManagerWithNonExistedFolder(TestFileSystemManagerParent):
    __mock_non_existed_table_folder = Path(__file__).parent.joinpath('pseudo-' + _FOLDER)

    def __init__(self, *args, **kwargs):
        self.__test_context = self._mock_tables_test(self.__mock_non_existed_table_folder, mkdir_=False)
        super().__init__(self.__test_context, *args, **kwargs)

    def test_delete_outdated_tables(self):
        self._do_delete_testing(self.__mock_non_existed_table_folder, '')
