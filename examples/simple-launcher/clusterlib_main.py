# clusterlib_main.py

import sys
import os
from clusterlib.storage import sqlite3_dumps
from main import main

NOSQL_PATH = os.path.join(os.environ["HOME"], "job.sqlite3")

if __name__ == "__main__":
    main()
    sqlite3_dumps({" ".join(sys.argv): "JOB DONE"}, NOSQL_PATH)
