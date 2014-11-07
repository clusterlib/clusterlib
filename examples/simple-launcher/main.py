# main.py

import sys, time

def main(argv=None):
    """A script with heavy computation"""
    if argv is None:
        argv = sys.argv  # For ease, function parameters are sys.argv

    # do heavy computation (usually based on argument)
    time.sleep(10)

    # Save script evaluation on the hard disk

if __name__ == "__main__":
    main()
