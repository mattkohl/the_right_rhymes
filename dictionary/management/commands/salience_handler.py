from dictionary.models import Sense


def main():

    senses = Sense.objects.filter(publish=True)
    for sense in senses:
        sense.remove_saliences()
        sense.add_saliences()
