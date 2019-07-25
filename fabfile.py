from fabric import task
from fabric.connection import Connection
import subprocess
import random

APP_REPO_URL = "https://github.com/mattkohl/the_right_rhymes.git"
XML_REPO_URL = "git@gitlab.com:mattkohl/django-xml.git"

###################################################################
# NB the below tasks require ~/.ssh/config to include configuration
# to connect to the server.
#
# e.g.
#
# Host foo
#   HostName 123.24.35.456
#   User foo
#   IdentityFile ~/.ssh/id_rsa
####################################################################


@task
def test_task(cxn):
    cxn.run("sudo ls", pty=True)


@task
def ingest(cxn):
    """
    To ingest with Fabric, execute this command: fab ingest
    """
    xml_source = "/home/{}/django-xml".format(cxn.user)
    venv = "/home/{}/.virtualenvs/the_right_rhymes".format(cxn.user)
    app_source = "/home/{}/the_right_rhymes".format(cxn.user)

    _get_latest_xml_source(cxn, xml_source)
    _ingest_dictionary(cxn, app_source, venv)


@task
def deploy(cxn):
    """
    To deploy with Fabric, execute this command: fab deploy
    """

    xml_source = f"/home/{cxn.user}/django-xml"
    venv = f"/home/{cxn.user}/.virtualenvs/the_right_rhymes"
    app_source = f"/home/{cxn.user}/the_right_rhymes"

    _get_latest_app_source(cxn, app_source, app_source)
    _update_settings(cxn, app_source, xml_source)
    _update_virtualenv(cxn, app_source, venv)
    _update_static_files(cxn, app_source, venv)
    _update_database(cxn, app_source, venv)
    _restart_gunicorn_service(cxn)


def _get_latest_app_source(cxn: Connection, source_folder, repo_url):
    if exists(source_folder + "/.git"):
        cxn.run(f"cd {source_folder} && git fetch")
    else:
        cxn.run(f"git clone {repo_url} {source_folder}")

    current_commit = subprocess.Popen("git log -n 1 --format=%H", shell=True)
    cxn.run("cd {} && git reset --hard {}".format(source_folder, current_commit))


def _get_latest_xml_source(cxn: Connection, source_folder):
    cxn.run("cd {} && git pull".format(source_folder))


def _update_settings(cxn: Connection, source_folder, xml_source):
    settings_path = source_folder + "/the_right_rhymes/settings.py"
    cxn.run(sed(settings_path, "DEBUG = True", "DEBUG = False"))
    cxn.run(sed(settings_path, "ALLOWED_HOSTS =.+$", """ALLOWED_HOSTS = ["www.therightrhymes.com", "therightrhymes.com"]"""))
    cxn.run(sed(settings_path, "SOURCE_XML_PATH =.+$", """SOURCE_XML_PATH = "{}" """.format(xml_source)))
    secret_key_file = source_folder + "/the_right_rhymes/secret_key.py"
    if not exists(secret_key_file):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '{}'".format(key))
    append(settings_path, "\nfrom .secret_key import SECRET_KEY")


def _update_virtualenv(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run("{}/bin/pip install --upgrade pip".format(virtualenv_folder))
    cxn.run("{}/bin/pip install -r {}/requirements.txt".format(virtualenv_folder, source_folder))


def _update_static_files(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run("cd {} && {}/bin/python manage.py collectstatic --noinput".format(source_folder, virtualenv_folder))


def _update_database(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run("cd {} && {}/bin/python manage.py migrate --noinput".format(source_folder, virtualenv_folder))


def _restart_gunicorn_service(cxn: Connection):
    cxn.run("sudo systemctl enable gunicorn", pty=True)
    cxn.run("sudo systemctl start gunicorn", pty=True)
    cxn.run("sudo systemctl restart gunicorn", pty=True)


def _ingest_dictionary(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run("cd {} && {}/bin/python manage.py ingest_dictionary".format(source_folder, virtualenv_folder))


def sed(filename: str, before: str, after: str) -> str:
    return f"sed -i s/{before}/{after}/g {filename}"


def exists(filename: str) -> str:
    return f"if [ -e {filename} ]; then echo 1; else echo 0; fi"


def append(filename: str, text: str) -> str:
    return f"echo '{text}' >> {filename}"


class DeployException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
