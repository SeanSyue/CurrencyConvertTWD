import re
import os
import requests

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


if __name__ == '__main__':
    download_csv()
