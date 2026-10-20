import pytest
import sys

if __name__ == "__main__":
    retcode = pytest.main(["tests/test_transformation.py"])
    sys.exit(retcode)
