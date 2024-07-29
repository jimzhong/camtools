import exifread
import os
import sys
import re
from send2trash import send2trash
from pprint import pprint


FILENAME_PATTERN = re.compile(r"^\w*\....$")

def should_remove(base, file):
    if FILENAME_PATTERN.fullmatch(file) is None:
        return False
    path = os.path.join(base, file).removesuffix(".ARW").removesuffix(".arw")
    for suffix in (".jpg", ".JPG", ".HEIF", ".heif", ".HEIC", ".heic", ".HIF", ".hif"):
        fname = path + suffix
        if os.path.isfile(fname):
            print("{} exists".format(fname))
            return False
    return True

def main(base_path):
    files_to_remove = []
    for root, _, files in os.walk(base_path):
        print("{} files in {}".format(len(files), root))
        raw_files = filter(lambda filename: filename.lower().endswith(".arw"), files)
        removes = filter(lambda filename: should_remove(root, filename), raw_files)
        for fname in removes:
            files_to_remove.append(os.path.join(root, fname))
    pprint(files_to_remove)
    send2trash(files_to_remove)
    print("{} files moved to trash".format(len(files_to_remove)))

if __name__ == '__main__':
    main(sys.argv[1])
