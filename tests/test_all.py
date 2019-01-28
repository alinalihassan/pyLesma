import os
import sys
import pytest
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
    proc = Popen([sys.executable, os.path.join(path, "src", "les.py"),
                 "run", os.path.join(path, "tests", "io", test_name + ".les")],
                 stdout=PIPE, stderr=PIPE, universal_newlines=True)
    out, err = proc.communicate()
    output = out.strip()
    error = err.strip()
    rc = proc.returncode

    assert 'Error:' not in error
    assert rc == 0

    if output:
        with open(os.path.join(path, "tests", "io", test_name + ".output"), newline=None) as expected:
            exp_str = "".join(expected.readlines())
            assert output == exp_str
