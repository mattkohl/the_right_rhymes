import sys


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50, filename=''):
    """
    Call in a loop to create terminal progress bar

    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    if filename:
        sys.stdout.write(f'\r{filename}\n{prefix} |{bar}| {percents}% {suffix}'),
    else:
        sys.stdout.write(f'{prefix} |{bar}| {percents}% {suffix}'),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


if __name__ == "__main__":
    from time import sleep

    # A List of Items
    items = list(range(0, 57))
    test = len(items)

    # Initial call to print 0% progress
    print_progress(0, test, prefix='Progress:', suffix='Complete', bar_length=50)
    for i, item in enumerate(items):
        sleep(0.1)
        print_progress(i+1, test, prefix='Progress:', suffix='Complete', bar_length=50)
