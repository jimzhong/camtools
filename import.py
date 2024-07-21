import exifread
import os
import sys
import filecmp
from datetime import datetime
from pprint import pprint

MAX_COUNT = 10000;
FILENAME_PATTERN = re.compile(r"^\w*\....$")
IMG_SUFFIXES = (".jpg", ".JPG", ".HEIF", ".heif", ".HEIC", ".heic", ".jpeg", ".JPEG", ".ARW", ".arw")

def file_is_image(filename):
    for s in IMG_SUFFIXES:
        if filename.endswith(s):
            return True
    return False
    
def get_earliest_stat_time(stat):
    t = min(stat.st_mtime, stat.st_ctime)
    try:
        t = min(t, stat.st_birthtime)
    except AttributeError:
        pass
    return datetime.fromtimestamp(t)
    
def get_date(filepath):
    with open(filepath, "rb") as f:
        tags = exifread.process_file(f, details=False)
        stat = os.fstat(f.fileno())
    try:
        timestamp_str = tags['EXIF DateTimeOriginal'].values
        timestamp = datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')
    except KeyError:
        print(filepath, "has no exif.")
        timestamp = get_earliest_stat_time(stat)
    return timestamp
    
def pad_month(month_str):
    if len(month_str) == 1:
        return '0' + month_str
    return month_str
    
def ensure_dir_exists(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        print("mkdir", path)
        
def file_have_same_data(f1, f2):
    return filecmp.cmp(f1, f2, shallow=False)
    
def move_file(source_path, dest_path):
    prefix, ext = os.path.splitext(dest_path)
    for count in range(1, MAX_COUNT):
        if dest_path == source_path:
            return None
        if not os.path.exists(dest_path) or file_have_same_data(source_path, dest_path):
            os.rename(source_path, dest_path)
            return dest_path
        # Reach here if dest_path exists and content differs
        dest_path = "{}_{}{}".format(prefix, count, ext)

def import_image(source_path, dest_root):
    date = get_date(source_path)
    dest_dir = os.path.join(dest_root, str(date.year), pad_month(str(date.month)))
    ensure_dir_exists(dest_dir)
    filename = os.path.split(source_path)[-1]
    dest_path = os.path.join(dest_dir, filename)
    actual_dest_path = move_file(source_path, dest_path)
    if actual_dest_path is None:
        print("same path", source_path)
    else:
        print("moved", source_path, "to", actual_dest_path)

def import_images(files, dest_dir):
    for f in files:
        import_image(f, dest_dir)

def main(source, dest_dir):
    for root, _, files in os.walk(source):
        img_files = [os.path.join(root, f) for f in files if file_is_image(f.lower())]
        print("{} images in {}".format(len(img_files), root))
        import_images(img_files, dest_dir)
        

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
