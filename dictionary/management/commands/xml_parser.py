import time
import sys
import logging

from geopy.geocoders import Nominatim

from dictionary.ingestion.directory_loader import DirectoryLoader
from dictionary.utils import update_stats

logger = logging.getLogger(__name__)


geolocator = Nominatim(user_agent=__name__)
geocache = []


CHECK_FOR_UPDATES = True


def main(directory):
    print(f"Parsing directory {directory}")
    start = time.time()
    xml_files = sorted(DirectoryLoader.collect_files(directory), key=lambda f: f.lower())
    DirectoryLoader.process(xml_files)
    end = time.time()
    total_time = end - start
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)

    msg = 'Processed dictionary in %d:%02d:%02d\n' % (h, m, s)
    logger.info(msg)
    sys.stdout.write(msg)
    update_stats()
