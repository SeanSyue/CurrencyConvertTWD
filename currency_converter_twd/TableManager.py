import re
import os
import configparser
import requests

config_file = 'currency_converter_twd/config.ini'
config = configparser.ConfigParser()
config.read(config_file)

URL = config['TABLE']['url']


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
                csv_file = csv_downloader(folder, url=URL)
                return csv_file
            except FileNotFoundError:
                print("[ERROR] Can not find currency exchange table file in {}! "
                      "Please check network connectivity, "
                      "then rerun this program to auto download a new file".format(folder))
                raise


def csv_downloader(folder, url=URL):
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
