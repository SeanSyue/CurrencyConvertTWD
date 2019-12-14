import re
import os
import configparser
from typing import List
from pathlib import Path

import requests

config = configparser.ConfigParser()
config.read('currency_converter_twd/config.ini')

# Location of online currency exchange table
_URL = config['TABLE']['url']

# The directory which currency exchange rate table is downloaded and stored
_FOLDER = config['TABLE']['folder']


class FileSystemManager:
    __active_table: str
    __outdated_tables: List[str]

    def __init__(self, root_):
        """
        Store names of different currency tables in the file system
        @var self.__active_table: names of active currency table
        @var self.__outdated_tables: names of outdated currency table
        @param root_: str or PathLike object. root directory where table folder exists
        """
        self.__active_table = ''
        self.__outdated_tables = list()
        self.__table_folder = Path(root_).joinpath(_FOLDER)

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
        if not isinstance(tables, list):
            raise TypeError("Variable `outdated_tables` should be initialized with an list object!")

        # empty `self.__outdated_tables` before re-populating
        if len(self.__outdated_tables) is not 0:
            self.__outdated_tables = list()
        self.__outdated_tables = tables

    @active_table.setter
    def active_table(self, table):
        """
        set new active currency table, and move the previous one into the `__outdated_tables` list
        @param table: names of new currency table
        """
        if self.__active_table is not '':
            self.__outdated_tables.append(self.__active_table)
        self.__active_table = table

    def initialize_table_folder(self):
        """
        initialize currency table under certain directory
        """
        # TODO: if `self.__table_folder` is not existed, then mkdir
        pass

    def translate_to_abs_table_path(self, name_):
        """
        translate to the absolute pathname of a currency table
        by referencing the file system
        @param name_: the name of a currency table
        @return: PathLike object
        """
        return self.__table_folder.joinpath(name_)

    @staticmethod
    def get_relevant_table_name(path_):
        """
        get the name of a currency table by referencing the file system
        @param path_: the absolute filepath of a currency table
        @return: str object
        """
        return Path(path_).name

    def delete_outdated_tables(self):
        # TODO: For tables in self.outdated_tables, do delete
        # TODO: self.outdated_tables = list()
        # TODO: Catch `FileNotFoundError`
        pass


class OnlineResourceManager:
    __url = _URL

    def __init__(self):
        self.__resource = None
        self.__resource_table_name = None

    def __query_table_resource(self):
        """
        post online currency table url, used for checking connectivity
        @return status code
        """
        # TODO: with requests.Session(), post `__url`, if network connections failed, return status code
        # TODO: if code==200, self.__resource = resource
        pass

    def __parse_resource_table_name(self):
        """
        @return return the name of the queried currency table for the resource
        """
        # TODO: _get_resource_table_name using `re` module
        # TODO: self.__resource_table_name = resource_table_name
        pass

    def fetch_latest_table_name(self):
        """
        wrapper function.
        """
        self.__query_table_resource()
        # TODO: if status == 200, `self.__parse_resource_table_name()`
        pass

    def download_table(self, destination_):
        """
        download a new table from the online resource
        @param destination_: the destination pathname of the newly downloaded table
        """
        # TODO: download currency table to target
        pass


class TableManager:

    def __init__(self):
        self.__sys_mgr = FileSystemManager(Path(__file__).parent)
        self.__res_mgr = OnlineResourceManager()

    def initialize(self):
        # TODO: Check if table folder exists
        # TODO: if not, `self.__sys_mgr.initialize_table_folder(Path(__file__).parent)`
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
        if len(self.__sys_mgr.outdated_tables) is 0:
            print("No outdated tables detected")
            return 'OK'
        else:
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
