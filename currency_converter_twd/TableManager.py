import re
import os
import configparser
import warnings
from typing import Set
from pathlib import Path

import requests
from requests.exceptions import Timeout, RequestException

config = configparser.ConfigParser()
config.read('currency_converter_twd/config.ini')

# Location of online currency exchange table
_URL = config['TABLE']['url']

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']


class TableCaches:
    __active_table: str
    __outdated_tables: Set[str]

    def __init__(self):
        """
        Store names of different currency tables in the file system
        @var self.__active_table: names of active currency table
        @var self.__outdated_tables: names of outdated currency table
        """
        self.__active_table = ''
        self.__outdated_tables = set()

    @property
    def outdated_tables(self):
        return self.__outdated_tables

    @property
    def active_table(self):
        return self.__active_table

    @outdated_tables.setter
    def outdated_tables(self, tables):
        """
        initialize self.__outdated_tables with list of table names
        @param tables: names of outdated currency table
        """
        if not isinstance(tables, set):
            raise TypeError("Variable `outdated_tables` should be initialized with a set object!")

        # empty `self.__outdated_tables` before re-populating
        if len(self.__outdated_tables) == 0:
            self.__outdated_tables = set()
        self.__outdated_tables = tables

    @active_table.setter
    def active_table(self, table):
        """
        set new active currency table, and move the previous one into the `__outdated_tables` list
        @param table: names of new currency table
        """
        if not isinstance(table, str):
            raise TypeError("Variable `active_table` should be initialized with a str object!")

        if self.__active_table != '':
            self.__outdated_tables.add(self.__active_table)
        self.__active_table = table


class FileSystemManager:

    def __init__(self, folder_name_):
        """
        Handles operations on file system level
        @param folder_name_: str or PathLike object. destination where table folder exists
        """

        self.__table_folder = Path(folder_name_)
        self.__table_caches = TableCaches()

        # initialize a workspace once the instance is made
        self.__initialize_table_folder()

    # expose some of the properties for external calls
    @property
    def table_folder(self):
        return self.__table_folder

    @property
    def outdated_tables(self):
        return self.__table_caches.outdated_tables

    @outdated_tables.setter
    def outdated_tables(self, value):
        self.__table_caches.outdated_tables = value

    @property
    def active_table(self):
        return self.__table_caches.active_table

    @active_table.setter
    def active_table(self, value):
        self.__table_caches.active_table = value

    def __initialize_table_folder(self):
        """
        initialize currency table under certain directory
        set `self.active_table` and `self.outdated_tables` respectively
        """
        # TODO: log init table folder
        self.__table_folder.mkdir(exist_ok=True)
        all_tables = {self.get_relevant_table_name(table) for table in self.__table_folder.glob('*.csv')}
        self.outdated_tables = all_tables
        self.active_table = max(all_tables, default='')
        # discard `active_table` from `outdated_tables`
        self.outdated_tables.discard(self.active_table)

    def translate_to_abs_table_path(self, name_):
        """
        translate to the absolute pathname of a currency table
        by referencing the file system
        @param name_: the name of a currency table
        @return: str object
        """
        return str(self.__table_folder.joinpath(name_))

    @staticmethod
    def get_relevant_table_name(path_):
        """
        get the name of a currency table by referencing the file system
        @param path_: the absolute filepath of a currency table
        @return: str object
        """
        return Path(path_).name

    def delete_outdated_tables(self, quick_run=True):
        """
        delete outdated table files according to table caches
        @param quick_run: if set to False, re-initialize table caches
        """
        # TODO: log `FileNotFoundError`
        if not quick_run:  # re-initialize workspace
            self.__initialize_table_folder()
        for table in self.__table_caches.outdated_tables:
            Path(self.translate_to_abs_table_path(table)).unlink(missing_ok=True)
        # Reset outdated tables
        self.__table_caches.outdated_tables = set()


class OnlineResourceManager:
    __url = _URL

    def __init__(self):
        self.__resource = None
        self.__resource_table_name = None

    # expose local variables
    @property
    def resource_table_name(self):
        return self.__resource_table_name

    @property
    def resource(self):
        return self.__resource

    def fetch_latest_resource(self):
        """
        request for the latest table resource
        if connection was success, analyse the resource
        if resource was correct, set `self.__resource` and `self.__resource_table_name` explicitly
        else, reset `self.__resource` and `self.__resource_table_name`
        """
        def analyse_resource(resource_):
            """
            if resource is correct, extract the table name from the resource
            else, set both `self.__resource` and `self.__resource_table_name` as none
            @return return original source if source is correct, else return none
            @return return the name of the queried currency table for the resource if the source is correct
            """
            # if `resource_` is none, set both `self.__resource` and `self.__resource_table_name` as none
            if resource_ is None:
                return None, None

            content = resource_.headers['Content-Disposition']
            pattern = r'"(.*?)"'
            match = re.search(pattern, content)
            try:
                table_name = match.group(1)
            # if match is None, set both `self.__resource` and `self.__resource_table_name` as none
            except AttributeError:
                warnings.warn("Table name is set to be value `None`! Should check for resource correctness! ")
                return None, None

            # if matched, return `self.__resource` and set `self.__resource_table_name` correspondingly
            return resource_, table_name

        # query for latest resources
        try:
            self.__resource = requests.get(self.__url, stream=True)
        except Timeout:
            warnings.warn("Oops! timeout!")
        except RequestException as e:
            warnings.warn(f"Connection failed with {e}")

        # if response was success, analyse the resource
        # TODO: handle more connection errors
        # TODO: log requesting
        self.__resource, self.__resource_table_name = analyse_resource(self.__resource)

    def download_table(self, destination_):
        """
        download a new table from the online resource
        @param destination_: the destination pathname of the newly downloaded table
        """
        p_destination = Path(destination_)
        if not p_destination.exists():
            raise FileNotFoundError(f"{destination_} does not exists!")

        if self.__resource and self.__resource_table_name is not None:
            with p_destination.join(self.__resource_table_name).open('wb') as csv:
                for chunk in self.__resource.iter_content(chunk_size=1024):
                    csv.write(chunk)
                # TODO: log complete
            # reset local variables
            self.__resource = None
            self.__resource_table_name = None
        else:
            raise ValueError("Should fetch latest resource first!")


class TableManager:

    def __init__(self):
        self.__sys_mgr = FileSystemManager(Path(__file__).parent.joinpath(_FOLDER))
        self.__res_mgr = OnlineResourceManager()

    def initialize(self):
        # TODO: Check if table folder exists
        # TODO: if not, `self.__sys_mgr.__initialize_table_folder(Path(__file__).parent)`
        # TODO: populate `self.__sys_mgr.active_table`
        # TODO: and `self.__sys_mgr.active_table`
        # TODO: with existing table files
        pass

    def update(self):
        # TODO: check if new
        # TODO: download
        # TODO: renew self.active_table
        pass

    def clean_up(self):
        self.__sys_mgr.delete_outdated_tables()


def csv_finder(folder):
    """
    Get newest exchange rate table file
    If no file exist in folder, then download a new one
    """
    for _, _, f in os.walk(folder):
        if f:
            return get_newest_file(folder)

        if not f:
            print("[INFO] Auto downloading currency exchange rate table file")
            try:
                csv_file = csv_downloader(folder, url=_URL)
                return csv_file
            except FileNotFoundError:
                print("[ERROR] Can not find currency exchange table file in {}! "
                      "Please check network connectivity, "
                      "then rerun this program to auto download a new file".format(folder))
                raise


def csv_downloader(folder, url=_URL):
    """
    Download latest exchange rate table and return the file name
    Note: this function don't check if newest file exist
    """
    with requests.Session() as session:
        print("[INFO] Fetching download site: {}".format(url))
        post = session.post(url)
        if post.status_code == 200:
            print("[INFO] Requesting download site: {}".format(url))
            res = session.get(url, stream=True)

            # Get filename from header retrieved
            content = res.headers['Content-Disposition']
            file_name = re.search(r'"(.*?)"', content).group(1)

            # # If file already up to date, then no need to download a new one
            # if file_name == get_newest_file(folder):
            #     print("[INFO] Existing file {} already up to date".format(file_name))

            # Download file if needed
            # elif res.status_code == 200:
            if res.status_code == 200:
                print('[INFO] Downloading file: "{}"'.format(file_name))
                with open(os.path.join(folder, file_name), 'wb') as csv:
                    for chunk in res.iter_content(chunk_size=1024):
                        csv.write(chunk)
                print("[INFO] Download completed")

            # return newest file name
            return file_name

        else:
            print("[ERROR] Post failed with status code: {}".format(post.status_code))
            raise FileNotFoundError


def get_newest_file(folder):
    return max(os.listdir(folder))


if __name__ == '__main__':
    """ TEST COMMANDS """
    # csv_downloader()
    # print(get_newest_file(DOWNLOAD_FOLDER))
