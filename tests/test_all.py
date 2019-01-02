import os
import pytest
from subprocess import Popen, PIPE


def get_tests():
    tests = []
    for file in os.listdir("./tests/io"):
        if file.endswith(".les"):
            tests.append(os.path.basename(file).split('.')[0])

    return tests


# Base test for all files
@pytest.mark.parametrize("test_name", get_tests())
def test_base(test_name):
    proc = Popen(["python3", "src/les.py", "run", f'tests/io/{test_name}.les'], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    output = out.decode('utf-8').strip()
    error = err.decode('utf-8').strip()
    rc = proc.returncode

    assert 'Error:' not in error
    assert rc == 0

    if output:
        with open(f'tests/io/{test_name}.output') as expected:
            exp_str = "".join(expected.readlines())
            assert output == exp_str
            expected.close()
