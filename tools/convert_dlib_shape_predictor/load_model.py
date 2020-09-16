import sys
import os
import dlib
import glob

def main():
    if len(sys.argv) != 2:
        exit()
    predictor = dlib.shape_predictor(sys.argv[1])
    return 0

if __name__ == '__main__':
    exit(main())
