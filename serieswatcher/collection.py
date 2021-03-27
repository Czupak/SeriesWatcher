import os
import glob
import re
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


class Collection:
    def __init__(self, path):
        self.path = path
        self.files = []
        self.collection = {}
        self.scan()
        self.map = {'The.End.of.the.F...ing.World': 'The End of the F...ing World',
                    'The.Drew.Carey.Show.Complete.DVDRip.XviD-ST': 'The Drew Carey Show',
                    'The.A-TEAM.1983.S01-S05.iNTERNAL.DVDRip.x264-DEUTERiUM': 'The A-TEAM',
                    'Stargate.SG-1.S02.PACK.PL.1080p.WEBRiP.x264-PTRG': 'Stargate SG-1',
                    'Sliders.S01-S05.iNTERNAL.DVDRip.x264-SCENE': 'Sliders',
                    'Mythic Quest - Ravens Banquet (2020) S01 REPACK (1080p ATVP Webrip x265 10bit EAC3 5.1 Atmos - Goki)[TAoE]': 'Mythic Quest',
                    'Married.with.Children.NTSC.DVD.DD2.0.MPEG-2.REMUX-S0NNY': 'Married with Children'}

    def scan(self):
        struct = []
        struct += get_files(self.path)
        self.files = sorted(struct)
        # self.discover_show()

    def discover_show(self, show_name, episode_key):
        def similar(a, b):
            p = round(SequenceMatcher(None, a, b).ratio(), 2)
            return p

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
