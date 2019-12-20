import configparser
import shutil
from filecmp import cmp
from unittest import TestCase
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import Mock, patch

from requests.exceptions import Timeout, RequestException

from currency_converter_twd.TableManager import TableCaches, FileSystemManager, OnlineResourceManager, TableManager

config = configparser.ConfigParser()
config.read('currency_converter_twd/config.ini')

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']

# param related to requests header
_FAKE_CONTENT_DISPOSITION = 'fake_content'
_CONTENT_DISPOSITION_TEMPLATE = 'attachment; filename="{}"'

# file paths to testing table files
_TEST_CSV_OLD_1 = 'currency_converter_twd/mock_tables/ExchangeRate@201912021600.csv'
_TEST_CSV_OLD_2 = 'currency_converter_twd/mock_tables/ExchangeRate@201912201451.csv'
_TEST_CSV_NEW = 'currency_converter_twd/mock_tables/ExchangeRate@201912201528.csv'


class Common:

    @staticmethod
    def make_response_mock(csv: str):
        """
        make mock response by referencing the testing table files
        @param csv: path to testing table file
        @return a `Mock()` object
        """

        p_mock_csv = Path(csv)
        mock_csv_name = Path(p_mock_csv).name
        mock_table_content = p_mock_csv.read_bytes()  # read csv file

        response_mock = Mock()
        response_mock.return_value.headers = {
            'Content-Disposition': _CONTENT_DISPOSITION_TEMPLATE.format(mock_csv_name)}
        response_mock.return_value.content = mock_table_content

        return response_mock


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
        self.assertEqual('new_2', self.__table_caches.active_table)
        # Check if `outdated_tables` caches previous `active_table`
        self.assertEqual({'existed_1', 'existed_2', 'new_1'}, self.__table_caches.outdated_tables)


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
        self.assertEqual(expected_active_table_, self.__sys_mgr.active_table)
        self.assertEqual(0, len(self.__sys_mgr.outdated_tables))

        # check if only expected active table remain in the folder
        indices = list(Path(folder_).glob('*.csv'))
        remaining_tables = [n.name for n in Path(folder_).glob('*.csv')] if indices else ['']
        self.assertEqual(1, len(remaining_tables))
        self.assertEqual(expected_active_table_, remaining_tables[0])

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
        fake_mock.headers = {'Content-Disposition': _FAKE_CONTENT_DISPOSITION}

        test_cases = [Timeout, RequestException, fake_mock]
        requests_mock.get.side_effect = test_cases

        # loop for testing cases
        for n in range(len(test_cases)):
            self.assertWarns(UserWarning, self.__res_mgr.fetch_latest_resource)
            self.assertIsNone(self.__res_mgr.resource)
            self.assertIsNone(self.__res_mgr.resource_table_name)

        # check if requests function was called correctly
        self.assertEqual(len(test_cases), requests_mock.get.call_count)

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_download_table(self, requests_mock):

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

        p_mock_csv = Path(_TEST_CSV_OLD_1)
        mock_csv_name = Path(p_mock_csv).name

        requests_mock.get.side_effect = Common.make_response_mock(_TEST_CSV_OLD_1)
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
            self.assertEqual(1, requests_mock.get.call_count)


class TestTableManagerParent(TestCase):
    p_folder = Path(__file__).parent.joinpath(_FOLDER)

    @contextmanager
    def _mock_tables_test(self, *tables_):
        """
        wrapper for setup and teardown
        makes mocked tables as workspace
        set "TableManager" instance for testing
        remove folder generated during tearing down
        @param tables_: mocked tables
        """

        def __make_existed_tables(folder_, *tables):
            for test_csv in tables:
                src = str(Path(test_csv).resolve())
                des = str(folder_.joinpath(Path(test_csv).name))
                shutil.copy(src, des)

        try:
            # TODO: log file making
            self.p_folder.mkdir(exist_ok=True)
            __make_existed_tables(self.p_folder, *tables_)
            self._tm = TableManager()
            yield
        finally:
            # TODO: log file deleting
            shutil.rmtree(self.p_folder)

    def _common_checks(self, expected_active_table, expected_outdated_tables):
        # Check if table folder really exists
        self.assertTrue(self.p_folder.exists())
        # inspect internal parameters of the `FileSystemManager`
        self.assertEqual(expected_active_table, self._tm.active_table)
        self.assertEqual(expected_outdated_tables, self._tm.outdated_tables)
        # inspect internal parameters of the `OnlineResourceManager`
        self.assertIsNone(self._tm.resource)
        self.assertIsNone(self._tm.resource_table_name)

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


class TestTableManagerWithEmptyFolder(TestTableManagerParent):

    def __init__(self, *args, **kwargs):
        self.__test_context = self._mock_tables_test()
        super().__init__(self.__test_context, *args, **kwargs)

    def test_init_with_empty_folder(self):
        """
        test if table folder is empty during the init phase
        """
        self._common_checks('', set())


class TestTableManagerWithExistingTables(TestTableManagerParent):
    mock_existing_tables = (_TEST_CSV_OLD_1, _TEST_CSV_OLD_2)

    def __init__(self, *args, **kwargs):
        self.__test_context = self._mock_tables_test(*self.mock_existing_tables)
        super().__init__(self.__test_context, *args, **kwargs)

    def test_init_with_tables_existing(self):
        """
        test if internal parameters is set correctly if some tables already existed during the init phase
        """
        self._common_checks(Path(_TEST_CSV_OLD_2).name, {Path(_TEST_CSV_OLD_1).name})

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_if_no_update(self, requests_mock):
        """
        test fetch update and if no update is detected
        """

        requests_mock.get.side_effect = Common.make_response_mock(_TEST_CSV_OLD_2)

        orig_tables = list(self.p_folder.glob('*.csv'))
        self._tm.update()
        new_tables = list(self.p_folder.glob('*.csv'))
        self.assertEqual(len(orig_tables), len(new_tables))
        # TODO: check if `download_table` was not called
        self._common_checks(Path(_TEST_CSV_OLD_2).name, {Path(_TEST_CSV_OLD_1).name})

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_download_new(self, requests_mock):
        """
        test fetch update and download new currency table
        """
        p_mock_csv = Path(_TEST_CSV_NEW)
        mock_csv_name = p_mock_csv.name

        requests_mock.get.side_effect = Common.make_response_mock(_TEST_CSV_NEW)

        orig_tables = list(self.p_folder.glob('*.csv'))
        self._tm.update()
        new_tables = list(self.p_folder.glob('*.csv'))
        self.assertEqual(len(orig_tables) + 1, len(new_tables))
        # TODO: check if `download_table` was called once
        self._common_checks(mock_csv_name, {Path(_TEST_CSV_OLD_1).name, Path(_TEST_CSV_OLD_2).name})

    @patch('currency_converter_twd.TableManager.requests', autospec=True)
    def test_download_new_with_cleanup(self, requests_mock):
        """
        test clean up
        """
        p_mock_csv = Path(_TEST_CSV_NEW)
        mock_csv_name = p_mock_csv.name

        requests_mock.get.side_effect = Common.make_response_mock(_TEST_CSV_NEW)

        orig_tables = list(self.p_folder.glob('*.csv'))
        self.assertEqual(len(self.mock_existing_tables), len(orig_tables))
        self._tm.update(clear=True)
        new_tables = list(self.p_folder.glob('*.csv'))
        self.assertEqual(1, len(new_tables))
        # TODO: check if `download_table` was called once
        self._common_checks(mock_csv_name, set())
