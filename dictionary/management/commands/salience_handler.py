from dictionary.models import Sense
from dictionary.management.commands.utils import print_progress, is_ascii
import logging


logger = logging.getLogger(__name__)


def main():

    senses = Sense.objects.filter(publish=True).order_by("headword")
    iterations = senses.count()
    print_progress(0, iterations, prefix='Progress:', suffix='Complete')
    for i, sense in enumerate(senses):
        msg = ""

        if is_ascii(str(sense)):
            msg = "Now processing: {}".format(str(sense))
        logger.info(msg)
        sense.remove_saliences()
        sense.add_saliences()

        print_progress(i+1, iterations, prefix='Progress:', suffix='Complete ({})'.format(msg))


