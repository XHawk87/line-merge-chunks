import select
import time
import unittest
from subprocess import Popen, PIPE


# noinspection DuplicatedCode
class TestMergeLines(unittest.TestCase):

    def setUp(self):
        self.script_path = './line-merge-chunks'

    def _run_script(self, cmd_args, input_str):
        p = Popen([self.script_path] + cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate(input=input_str.encode())
        return p.returncode, out.decode(), err.decode()

    def test_empty_input(self):
        rc, out, err = self._run_script([], '')

        self.assertEqual('', err)
        self.assertEqual(0, rc)
        self.assertEqual('', out)

    def test_eof_on_incomplete_line(self):
        rc, out, err = self._run_script([], 'incomplete line')

        self.assertEqual('', err)
        self.assertEqual(0, rc)
        self.assertEqual('incomplete line\n', out)

    def test_single_line_input(self):
        rc, out, err = self._run_script([], 'hello world\n')
        self.assertEqual('', err)
        self.assertEqual(0, rc)
        self.assertEqual('hello world\\n\n', out)

    def test_multi_line_input(self):
        input_str = '''line 1
line 2
line 3
'''
        rc, out, err = self._run_script([], input_str)
        self.assertEqual('', err)
        self.assertEqual(0, rc)
        self.assertEqual('line 1\\nline 2\\nline 3\\n\n', out)

    def test_max_chars_break_on_new_lines(self):
        input_str = '''this
is
a
long multi-line
text
'''
        rc, out, err = self._run_script(['--max-chars', '20'], input_str)
        self.assertEqual('', err)
        self.assertEqual(0, rc)
        out_lines = out.splitlines(keepends=True)
        self.assertGreaterEqual(len(out_lines), 1)
        self.assertEqual('this\\nis\\na\\n\n', out_lines[0])
        self.assertGreaterEqual(len(out_lines), 2)
        self.assertEqual('long multi-line\\n\n', out_lines[1])
        self.assertGreaterEqual(len(out_lines), 3)
        self.assertEqual('text\\n\n', out_lines[2])
        self.assertEqual([], out_lines[3:])

    def test_max_chars_break_single_lines_on_space(self):
        input_str = '''this is a long line of text that should be broken up into smaller chunks by the script
'''
        rc, out, err = self._run_script(['--max-chars', '20'], input_str)
        self.assertEqual('', err)
        self.assertEqual(0, rc)
        out_lines = out.splitlines(keepends=True)
        self.assertGreaterEqual(len(out_lines), 1)
        self.assertEqual('this is a long \n', out_lines[0])
        self.assertGreaterEqual(len(out_lines), 2)
        self.assertEqual('line of text that \n', out_lines[1])
        self.assertGreaterEqual(len(out_lines), 3)
        self.assertEqual('should be broken \n', out_lines[2])
        self.assertGreaterEqual(len(out_lines), 4)
        self.assertEqual('up into smaller \n', out_lines[3])
        self.assertGreaterEqual(len(out_lines), 5)
        self.assertEqual('chunks by the \n', out_lines[4])
        self.assertGreaterEqual(len(out_lines), 6)
        self.assertEqual('script\\n\n', out_lines[5])
        self.assertEqual([], out_lines[6:])

    def test_max_chars_break_long_words(self):
        input_str = '''thisisalonglineofruntogethertextthatshouldbebrokenupintosmallerchunksbythescript
'''
        rc, out, err = self._run_script(['--max-chars', '20'], input_str)
        self.assertEqual('', err)
        self.assertEqual(0, rc)
        out_lines = out.splitlines(keepends=True)
        self.assertGreaterEqual(len(out_lines), 1)
        self.assertEqual('thisisalonglineofru\n', out_lines[0])
        self.assertGreaterEqual(len(out_lines), 2)
        self.assertEqual('ntogethertextthatsh\n', out_lines[1])
        self.assertGreaterEqual(len(out_lines), 3)
        self.assertEqual('ouldbebrokenupintos\n', out_lines[2])
        self.assertGreaterEqual(len(out_lines), 4)
        self.assertEqual('mallerchunksbythesc\n', out_lines[3])
        self.assertGreaterEqual(len(out_lines), 5)
        self.assertEqual('ript\\n\n', out_lines[4])
        self.assertEqual([], out_lines[5:])

    def test_max_time_output_immediately_on_eof(self):
        input_str = '''line 1
'''
        start_time = time.monotonic()
        rc, out, err = self._run_script(['--max-time', '2'], input_str)
        end_time = time.monotonic()

        self.assertEqual('', err)
        self.assertEqual(0, rc)
        self.assertLess(end_time - start_time, 0.1)

    def test_max_time_with_delay(self):
        # Launch script process as subprocess
        proc = Popen([self.script_path] + ['--max-time', '2'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

        # Write first block of input to script
        proc.stdin.write(b'block 1\n')
        proc.stdin.flush()

        # Start the timer on first input
        start_time = time.monotonic()

        # Wait for specified delay
        out_ready, _, _ = select.select([proc.stdout], [], [], 1)
        # Should still be waiting for more input at this point
        self.assertFalse(out_ready)

        # Write second block of input to script
        proc.stdin.write(b'block 2\n')
        proc.stdin.flush()

        # Wait for output ready
        out_ready, _, _ = select.select([proc.stdout], [], [], 1.1)
        # The first two blocks should have been flushed now
        self.assertTrue(out_ready)
        # And approximately 2 seconds should have passed
        self.assertGreaterEqual(time.monotonic() - start_time, 1.9)

        # Close standard input
        proc.stdin.close()
        rc = proc.wait(0.1)

        # Check there were no errors
        err = proc.stderr.read().decode()
        self.assertEqual('', err)
        self.assertEqual(0, rc)

        # Read from standard output
        out = proc.stdout.read().decode()

        # Check that output matches expected result
        self.assertEqual(out, 'block 1\\nblock 2\\n\n')


if __name__ == '__main__':
    unittest.main()
