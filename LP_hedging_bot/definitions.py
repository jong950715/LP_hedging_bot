import os


def getRootDir():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    return ROOT_DIR


def main():
    r = getRootDir()
    print(r)


if __name__ == "__main__":
    main()
