import os
from difflib import SequenceMatcher
from pprint import pprint


def get_files(subdir):
    contents = os.listdir(subdir)
    dirs = [os.path.join(subdir, i) for i in contents if os.path.isdir(os.path.join(subdir, i))]
    files = [os.path.join(subdir, i) for i in contents if os.path.isfile(os.path.join(subdir, i))]
    files = [i for i in files if i[-3:] in ['avi', 'mkv', 'mp4']]
    for my_dir in dirs:
        files = get_files(my_dir) + files
    return files


def similar(a, b):
    p = round(SequenceMatcher(None, a, b).ratio(), 2)
    return p


class Collection:
    def __init__(self, path):
        self.path = path
        self.files = []
        self.collection = {}
        self.scan()

    def validate(self):
        if self.path == '':
            return False
        return True

    def scan(self):
        if self.validate():
            struct = []
            struct += get_files(self.path)
            self.files = sorted(struct)

    def discover_show(self, show_name, episode_key):
        mem = ['', -999.00]
        for file in self.files:
            new_file = self.shorten_path_to_file(file)
            clean_file = file.lower().replace('.', ' ')
            clean_show_name = self.clean_show_name(show_name)
            parts = clean_file.split(os.path.sep)
            if len(parts) > 1:
                if clean_show_name == parts[0] and episode_key.lower() in clean_file:
                    mem = [new_file, 1.00]
                    break

            if clean_show_name in clean_file and episode_key.lower() in clean_file:
                mem = [new_file, 0.99]
                # break

            prob = similar(f"{show_name}.{episode_key}", new_file)
            if mem[1] < prob:
                mem = [new_file, prob]

        return mem

    def shorten_path_to_file(self, file):
        return file.replace(self.path + os.path.sep, '')

    def clean_show_name(self, show_name):
        if show_name == 'Stargate SG-1':
            return 'gwiezdne wrota'
        return show_name.lower().replace('\'', '').replace('...', '')

    def is_deleted(self, file):
        file_path = os.path.join(self.path, file)
        if os.path.isfile(file_path):
            return False
        return True

    def delete(self, file):
        file_path = os.path.join(self.path, file)
        print(f'Removing {file_path}')
        os.unlink(file_path)
