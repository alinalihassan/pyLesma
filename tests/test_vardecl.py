import unittest
from subprocess import Popen, PIPE


class TestVariableDeclaration(unittest.TestCase):
    def test_vardecl(self):
        proc = Popen(["python3", "src/les.py", "run", 'tests/io/vardecl.les'], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        output = out.decode('utf-8').strip()
        error = err.decode('utf-8').strip()
        rc = proc.returncode
        with open('tests/io/vardecl.output') as expected:
            exp_str = "".join(expected.readlines())
            self.assertTrue('Error:' not in error)
            self.assertTrue(output == exp_str)
            self.assertEqual(rc, 0)
            expected.close()


if __name__ == '__main__':
    unittest.main()
