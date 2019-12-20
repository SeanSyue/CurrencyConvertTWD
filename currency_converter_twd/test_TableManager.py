import configparser
import shutil
from filecmp import cmp
from unittest import TestCase
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import Mock, patch

from requests.exceptions import Timeout, RequestException

from currency_converter_twd.TableManager import TableCaches, FileSystemManager, OnlineResourceManager

config = configparser.ConfigParser()
config.read('currency_converter_twd/config.ini')

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']

_TEST_CSV_OLD = 'currency_converter_twd/mock_tables/ExchangeRate@201912021600.csv'
_TEST_CSV_NEW = 'currency_converter_twd/mock_tables/ExchangeRate@201912201451.csv'


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


class TestOnlineResourceManager(TestCase):

    def setUp(self) -> None:
        self.__res_mgr = OnlineResourceManager()

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_fetch_latest_table_name_if_error(self, requests_mock):
        # test if connection succeeded but content went wrong
        fake_mock = Mock()
        fake_mock.status_code = 200
        fake_mock.headers = {'Content-Disposition': 'fake_content'}

        test_cases = [Timeout, RequestException, fake_mock]
        requests_mock.get.side_effect = test_cases

        # loop for testing cases
        for n in range(len(test_cases)):
            self.assertWarns(UserWarning, self.__res_mgr.fetch_latest_resource)
            self.assertEqual(self.__res_mgr.resource, None)
            self.assertEqual(self.__res_mgr.resource_table_name, None)

        # check if requests function was called correctly
        self.assertEqual(requests_mock.get.call_count, len(test_cases))

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_download_table(self, requests_mock):
        def __read_mock_csv(csv_: Path):
            """
            return the content of the reference csv file
            @param csv_: path to the csv file found
            @return: the content the reference csv file
            """
            return csv_.read_bytes()

        @contextmanager
        def __mkdir_test_context(folder_):
            """
            make a temporary folder to contain 'downloaded' currency table
            delete the entire folder once the test is completed
            @param folder_: name of the temporary folder
            """
            try:
                # TODO: log file making
                folder_.mkdir(exist_ok=True)  # make mock table folder
                yield
            finally:
                # TODO: log file deleting
                shutil.rmtree(folder_)

        p_mock_csv = Path(_TEST_CSV_OLD)
        mock_table_content = __read_mock_csv(p_mock_csv)
        mock_csv_name = Path(p_mock_csv).name

        response_mock = Mock()
        response_mock.return_value.headers = {'Content-Disposition': f'attachment; filename="{mock_csv_name}"'}
        response_mock.return_value.content = mock_table_content

        requests_mock.get.side_effect = response_mock
        self.__res_mgr.fetch_latest_resource()

        # check if download destination folder not found
        with self.assertRaises(FileNotFoundError):
            self.__res_mgr.download_table(Path(__file__).parent.joinpath('non-existed-location'))

        # check if download successful
        mock_download_root = Path(__file__).parent.joinpath('mock-download-root')
        with __mkdir_test_context(mock_download_root):
            self.__res_mgr.download_table(mock_download_root)

            # check if csv file really exists
            mock_downloaded_csv = mock_download_root.joinpath(mock_csv_name)
            # check if file content is correct
            self.assertTrue(cmp(mock_downloaded_csv, p_mock_csv))
            # check if internal properties set correctly
            self.assertIsNone(self.__res_mgr.resource)
            self.assertIsNone(self.__res_mgr.resource_table_name)

            # check if requests function was called correctly
            self.assertEqual(requests_mock.get.call_count, 1)


class TestTableManager(TestCase):
    def test_if_no_update(self):
        """
        test fetch update and if no update is detected
        """
        pass

    def test_download_new(self):
        """
        test fetch update and download new currency table
        """
        pass

    def test_download_new_with_cleanup(self):
        """
        test clean up
        """
        pass
