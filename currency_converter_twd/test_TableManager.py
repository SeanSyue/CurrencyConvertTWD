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
        try:
            # TODO: log file making
            if mkdir_:  # make mock table folder
                folder_.mkdir(exist_ok=True)
                if tables_:  # generate mock tables
                    print(f"{tables_ = }")
                    for file in tables_:
                        folder_.joinpath(file).touch()
            self.__sys_mgr = FileSystemManager(folder_)
            yield
        finally:
            # TODO: log file deleting
            shutil.rmtree(folder_)

    def _do_delete_assertion(self, folder_, expected_active_table_):
        self.__sys_mgr.delete_outdated_tables()
        self.assertEqual(self.__sys_mgr.active_table, expected_active_table_)
        self.assertEqual(len(self.__sys_mgr.outdated_tables), 0)
        self.assertEqual([n.name for n in Path(folder_).glob('*.csv')][0], expected_active_table_)


class TestFileSystemManagerWithExistingTables(TestFileSystemManagerParent):
    __mock_table_folder = Path(__file__).parent.joinpath('test-' + _FOLDER)
    __mock_tables = [f'ExchangeRate@201912021{i}00.csv' for i in range(3, 6)]

    def test_delete_outdated_tables(self):
        """
        test if tables can be deleted correctly
        """
        print(f"{self.__mock_tables = }")
        with self._mock_tables_test(self.__mock_table_folder, *self.__mock_tables):
            # self._do_delete_assertion(self.__mock_table_folder, max(self.__mock_tables))
            self._do_delete_assertion(self.__mock_table_folder, 'ExchangeRate@201912021500.csv')


class TestFileSystemManagerWithEmptyFolder(TestFileSystemManagerParent):
    __mock_empty_table_folder = Path(__file__).parent.joinpath('empty-' + _FOLDER)

    def test_delete_outdated_tables(self):
        """
        test if tables can be deleted correctly
        """
        with self._mock_tables_test(self.__mock_empty_table_folder):
            self._do_delete_assertion(self.__mock_empty_table_folder, '')


class TestFileSystemManagerWithNonExistedFolder(TestFileSystemManagerParent):
    __mock_non_existed_table_folder = Path(__file__).parent.joinpath('pseudo-' + _FOLDER)

    def test_delete_outdated_tables(self):
        """
        test if tables can be deleted correctly
        """
        with self._mock_tables_test(self.__mock_non_existed_table_folder):
            self._do_delete_assertion(self.__mock_non_existed_table_folder, '')
