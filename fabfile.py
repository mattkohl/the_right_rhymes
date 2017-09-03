from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, sudo
import random

REPO_URL = "https://github.com/mattkohl/the_right_rhymes.git"


def deploy():
    """
    To deploy with Fabric, execute this command: fab deploy:host=username@hostname
    """
    source_folder = "/home/{}/the_right_rhymes".format(env.user)
    virtualenv_folder = "/home/{}/.virtualenvs/the_right_rhymes".format(env.user)

    _get_latest_source(source_folder)
    _update_settings(source_folder)
    _update_virtualenv(source_folder, virtualenv_folder)
    _update_static_files(source_folder, virtualenv_folder)
    _update_database(source_folder, virtualenv_folder)
    _restart_gunicorn_service()


def _get_latest_source(source_folder):
    if exists(source_folder + "/.git"):
        run("cd {} && git fetch".format(source_folder))
    else:
        run("git clone {} {}".format(REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run("cd {} && git reset --hard {}".format(source_folder, current_commit))


def _update_settings(source_folder):
    settings_path = source_folder + "/the_right_rhymes/settings.py"
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, "ALLOWED_HOSTS =.+$", "ALLOWED_HOSTS = ['www.therightrhymes.com', 'therightrhymes.com']")
    secret_key_file = source_folder + "/the_right_rhymes/secret_key.py"
    if not exists(secret_key_file):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '{}'".format(key))
    append(settings_path, "\nfrom .secret_key import SECRET_KEY")


def _update_virtualenv(source_folder, virtualenv_folder):
    run("{}/bin/pip install -r {}/requirements.txt".format(virtualenv_folder, source_folder))


def _update_static_files(source_folder, virtualenv_folder):
    run("cd {} && {}/bin/python manage.py collectstatic --noinput".format(source_folder, virtualenv_folder))


def _update_database(source_folder, virtualenv_folder):
    run("cd {} && {}/bin/python manage.py migrate --noinput".format(source_folder, virtualenv_folder))


def _restart_gunicorn_service():
    sudo("systemctl enable gunicorn")
    sudo("systemctl start gunicorn")
    sudo("systemctl restart gunicorn")


class DeployException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
