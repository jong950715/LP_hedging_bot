import os


def getRootDir():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return root_dir


def main():
    r = getRootDir()
    print(r)


if __name__ == "__main__":
    main()
