import os
import pytest
import tempfile
from subprocess import Popen, PIPE


def get_tests():
    tests = []
    path = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(path, "io")):
        if file.endswith(".les"):
            tests.append(os.path.basename(file).split('.')[0])

    return tests


# Base test for Lesma script files
@pytest.mark.parametrize("test_name", get_tests())
def test_base(test_name):
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    with tempfile.TemporaryDirectory() as dirpath:
        proc = Popen(["python3", os.path.join(path, "src", "les.py"),
                      "compile", os.path.join(path, "tests", "io", test_name + ".les"),
                      "-l", "-o", os.path.join(dirpath, "temp")],
                     stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        output = out.decode('utf-8').strip()
        error = err.decode('utf-8').strip()
        rc = proc.returncode

        assert 'Error:' not in error
        assert rc == 0
