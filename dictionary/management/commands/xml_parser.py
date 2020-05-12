import time
import sys
import logging


from dictionary.ingestion.directory_loader import DirectoryLoader
from dictionary.utils import update_stats

logger = logging.getLogger(__name__)


def main(directory: str, force_update: bool = False):
    print(f"Parsing directory {directory}")
    start = time.time()
    xml_files = sorted(DirectoryLoader.collect_xml_files(directory), key=lambda f: f.lower())
    DirectoryLoader.process_xml(xml_files, force_update)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    msg = 'Processed dictionary in %d:%02d:%02d\n' % (h, m, s)
    logger.info(msg)
    sys.stdout.write(msg)
    update_stats()
