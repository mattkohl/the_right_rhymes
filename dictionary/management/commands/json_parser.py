import time
import sys
import logging

from dictionary.ingestion.directory_loader import DirectoryLoader
from dictionary.utils import update_stats

logger = logging.getLogger(__name__)


def main(directory):
    print(f"Parsing directory {directory}")
    start = time.time()
    json_files = sorted(DirectoryLoader.collect_json_files(directory), key=lambda f: f.lower())
    DirectoryLoader.process_json(json_files)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    msg = 'Processed in %d:%02d:%02d\n' % (h, m, s)
    logger.info(msg)
    sys.stdout.write(msg)
    update_stats()
