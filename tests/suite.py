import unittest
from pathlib import Path

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('.', top_level_dir=Path('..'))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
