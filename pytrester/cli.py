import sys
from pytrester.tasks import enqueue_modules, test_py3


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_py3(sys.argv[1])
    else:
        enqueue_modules()
