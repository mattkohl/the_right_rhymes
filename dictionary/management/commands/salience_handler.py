from dictionary.models import Sense
import logging


logger = logging.getLogger(__name__)


def main():

    senses = Sense.objects.filter(publish=True)
    for sense in senses:
        msg = "Now processing: {}".format(sense)
        logger.info(msg)
        sense.remove_saliences()
        sense.add_saliences()
