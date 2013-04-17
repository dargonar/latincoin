#!/usr/bin/python
import optparse
import sys
# Install the Python unittest2 package before you run this script.
import unittest2

USAGE = """%prog SDK_PATH TEST_PATH PATTERN
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules
[PATTERN]   test_*.py default"""

def main(sdk_path, test_path, pattern):
    sys.path.insert(0, sdk_path)
    sys.path[0:0] = ['../appengine/lib', '../appengine/distlib', '../appengine', '../appengine/distlib/bitcoinrpc']

    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest2.loader.TestLoader().discover(test_path, pattern=pattern)
    unittest2.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) < 2:
        print 'Error: 2 arguments required.'
        parser.print_help()
        sys.exit(1)
    SDK_PATH = args[0]
    TEST_PATH = args[1]

    PATTERN = '*.py'
    if len(args) > 2:
        PATTERN = args[2]

    main(SDK_PATH, TEST_PATH, PATTERN)
