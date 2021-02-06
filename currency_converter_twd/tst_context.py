from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree


@contextmanager
def with_folder(name):
    try:
        p = Path(folder_name)
        p.mkdir(exist_ok=True)
        a_file = p.joinpath('a_file')
        a_file.touch()
        print(f"{a_file.resolve() = } \n created!")
        yield
    finally:
        rmtree(name)


if __name__ == '__main__':
    folder_name = 'a_folder'
    with with_folder(folder_name):
        print(Path(folder_name).exists())
        for n in Path(folder_name).iterdir():
            print(n)
