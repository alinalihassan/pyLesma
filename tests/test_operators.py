import unittest
from subprocess import Popen, PIPE


class TestArithmetic(unittest.TestCase):
    def test_arithmetic(self):
        proc = Popen(["python3", "src/les.py", "run", 'tests/io/operators.les'], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        output = out.decode('utf-8').strip()
        error = err.decode('utf-8').strip()
        rc = proc.returncode
        with open('tests/io/operators.output') as expected:
            self.assertTrue('Error:' not in error)
            self.assertEqual(rc, 0)
            expected.close()


if __name__ == '__main__':
    unittest.main()
