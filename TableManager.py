import re
import os
import time
import requests
import numpy as np

URL = 'http://rate.bot.com.tw/xrt/flcsv/0/day?Lang=en-US'
DOWNLOAD_FOLDER = 'exchange-rate-tables'


def download_csv(folder=DOWNLOAD_FOLDER):
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with requests.Session() as session:
        post = session.post(URL)
        if post.status_code == 200:
            res = session.get(URL, stream=True)
            content = res.headers['Content-Disposition']
            file_name = re.search(r'"(.*?)"', content).group(1)
            print('Downloading file: "{}"'.format(file_name))

            if res.status_code == 200:
                with open(os.path.join(folder, file_name), 'wb') as csv:
                    for chunk in res.iter_content(chunk_size=1024):
                        csv.write(chunk)
                print("Download completed")
        else:
            print("Post failed with status code: {}".format(post.status_code))


def search_newest_file(folder):
    def get_timestamp(target):
        time_str = re.search(r'@(.*?)\.', target).group(1)
        return time.strptime(time_str, '%Y%m%d%H%M')

    file_list = os.listdir(folder)
    return file_list[int(np.argmax(map(get_timestamp, file_list)))]


if __name__ == '__main__':
    download_csv()
