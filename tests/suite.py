import unittest
from pathlib import Path


def run_tests(path):
    testsuite = unittest.TestLoader().discover('.', top_level_dir=path)
    unittest.TextTestRunner(verbosity=2).run(testsuite)


if __name__ == '__main__':
    run_tests(Path('..'))
