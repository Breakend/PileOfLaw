# This script: checks that downloaded tar.gz files are valid.
import argparse
import glob
import os
import ujson

try:
    import lzma as xz
except ImportError:
    import pylzma as xz

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--raw_data', default='raw_data', help='path to raw data')


def check_files(args):
    path = os.path.join(args.raw_data, "*.xz")
    files = glob.glob(path)
    print(f"Found {len(files)} files.")
    failed = []
    errors = []
    for path in files:
        print(f"Trying {path}...", end="")
        try:
            with xz.open(path) as f:
                for line in f:
                    data = ujson.loads(line)
                    break
                print("SUCCEEDED")
        except Exception as e:
            errors.append(e)
            failed.append(path)
            print("FAILED")
    print(f"Failed on {failed}.")
    print(errors)


if __name__ == '__main__':
    args = parser.parse_args()
    check_files(args)