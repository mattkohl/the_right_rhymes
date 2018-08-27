from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, sudo
import random

APP_REPO_URL = "https://github.com/mattkohl/the_right_rhymes.git"
XML_REPO_URL = "git@gitlab.com:mattkohl/django-xml.git"


def ingest():
    """
    To ingest with Fabric, execute this command: fab ingest:host=username@hostname
    """

    xml_source = "/home/{}/django-xml".format(env.user)
    venv = "/home/{}/.virtualenvs/the_right_rhymes".format(env.user)
    app_source = "/home/{}/the_right_rhymes".format(env.user)

    _get_latest_xml_source(xml_source)
    _ingest_dictionary(app_source, venv)


def deploy():
    """
    To deploy with Fabric, execute this command: fab deploy:host=username@hostname
    """

    xml_source = "/home/{}/django-xml".format(env.user)
    venv = "/home/{}/.virtualenvs/the_right_rhymes".format(env.user)
    app_source = "/home/{}/the_right_rhymes".format(env.user)

    _get_latest_app_source(app_source, app_source)
    _update_settings(app_source, xml_source)
    _update_virtualenv(app_source, venv)
    _update_static_files(app_source, venv)
    _update_database(app_source, venv)
    _restart_gunicorn_service()


def _get_latest_app_source(source_folder, repo_url):
    if exists(source_folder + "/.git"):
        run("cd {} && git fetch".format(source_folder))
    else:
        run("git clone {} {}".format(repo_url, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run("cd {} && git reset --hard {}".format(source_folder, current_commit))


def _get_latest_xml_source(source_folder):
    run("cd {} && git pull".format(source_folder))


def _update_settings(source_folder, xml_source):
    settings_path = source_folder + "/the_right_rhymes/settings.py"
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, "ALLOWED_HOSTS =.+$", """ALLOWED_HOSTS = ["www.therightrhymes.com", "therightrhymes.com"]""")
    sed(settings_path, "SOURCE_XML_PATH =.+$", """SOURCE_XML_PATH = "{}" """.format(xml_source))
    secret_key_file = source_folder + "/the_right_rhymes/secret_key.py"
    if not exists(secret_key_file):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '{}'".format(key))
    append(settings_path, "\nfrom .secret_key import SECRET_KEY")


def _update_virtualenv(source_folder, virtualenv_folder):
    run("{}/bin/pip install --upgrade pip".format(virtualenv_folder))
    run("{}/bin/pip install -r {}/requirements.txt".format(virtualenv_folder, source_folder))


def _update_static_files(source_folder, virtualenv_folder):
    run("cd {} && {}/bin/python manage.py collectstatic --noinput".format(source_folder, virtualenv_folder))


def _update_database(source_folder, virtualenv_folder):
    run("cd {} && {}/bin/python manage.py migrate --noinput".format(source_folder, virtualenv_folder))


def _restart_gunicorn_service():
    sudo("systemctl enable gunicorn")
    sudo("systemctl start gunicorn")
    sudo("systemctl restart gunicorn")


def _ingest_dictionary(source_folder, virtualenv_folder):
    run("cd {} && {}/bin/python manage.py ingest_dictionary".format(source_folder, virtualenv_folder))


class DeployException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
