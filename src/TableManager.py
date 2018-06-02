import re
import os
import requests

URL = 'http://rate.bot.com.tw/xrt/flcsv/0/day?Lang=en-US'
DOWNLOAD_FOLDER = '../exchange-rate-tables'
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def csv_downloader(folder=DOWNLOAD_FOLDER, url=URL):
    # # If download folder is not existed, then create a new one
    # if not os.path.isdir(folder):
    #     os.makedirs(folder)

    with requests.Session() as session:
        print("[INFO] Fetching download site: {}".format(url))
        post = session.post(url)
        if post.status_code == 200:
            print("[INFO] Requesting download site: {}".format(url))
            res = session.get(url, stream=True)

            # Get filename from header retrieved
            content = res.headers['Content-Disposition']
            file_name = re.search(r'"(.*?)"', content).group(1)

            # If file already up to date, then no need to download a new one, just return
            if file_name == search_newest_file(folder):
                print("[INFO] Existing file {} already up to date".format(file_name))

            # Download file if needed
            elif res.status_code == 200:
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


def search_newest_file(folder):
    # Check if folder is empty
    for _, _, files in os.walk(folder):
        if not files:
            return None
        else:
            return max(os.listdir(folder))

    # try:
    #     newest = max(os.listdir(folder))
    # except ValueError:  # if no file is found
    #     raise FileNotFoundError
    # return newest


if __name__ == '__main__':
    """ TEST COMMANDS """
    csv_downloader()
    print(search_newest_file(DOWNLOAD_FOLDER))
