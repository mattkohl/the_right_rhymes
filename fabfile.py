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
# Host trr
#   HostName 123.24.35.456
#   User foo
#   IdentityFile ~/.ssh/id_rsa
####################################################################


@task
def test_task(cxn):
    print(cxn)


@task
def ingest(cxn):
    """
    To ingest with Fabric, execute this command: fab  -H trr ingest
    """
    xml_source = f"/home/{cxn.user}/django-xml"
    venv = f"/home/{cxn.user}/.virtualenvs/the_right_rhymes"
    app_source = f"/home/{cxn.user}/the_right_rhymes"

    _get_latest_xml_source(cxn, xml_source)
    _ingest_dictionary(cxn, app_source, venv)


@task
def deploy(cxn):
    """
    To deploy with Fabric, execute this command: fab -H trr deploy
    """

    xml_source = f"/home/{cxn.user}/django-xml"
    venv = f"/home/{cxn.user}/.virtualenvs/the_right_rhymes"
    app_source = f"/home/{cxn.user}/the_right_rhymes"

    _get_latest_app_source(cxn, app_source)
    _update_settings(cxn, app_source, xml_source)
    _update_virtualenv(cxn, app_source, venv)
    _update_static_files(cxn, app_source, venv)
    _update_database(cxn, app_source, venv)
    _restart_gunicorn_service(cxn)
    print(f"Done!")


def _get_latest_app_source(cxn: Connection, source_folder):
    cxn.run(f"cd {source_folder} && git pull")


def _get_latest_xml_source(cxn: Connection, source_folder):
    cxn.run(f"cd {source_folder} && git pull")


def _update_settings(cxn: Connection, source_folder, xml_source):
    settings_path = f"{source_folder}/the_right_rhymes/settings.py"
    cxn.run(sed(settings_path, "DEBUG = True", "DEBUG = False"))
    cxn.run(sed(settings_path, "ALLOWED_HOSTS =.+$", """ALLOWED_HOSTS = ["www.therightrhymes.com", "therightrhymes.com"]"""))
    cxn.run(sed(settings_path, "SOURCE_XML_PATH =.+$", f"""SOURCE_XML_PATH = "{xml_source}" """))
    secret_key_file = f"{source_folder}/the_right_rhymes/secret_key.py"
    if not cxn.run(exists(secret_key_file)):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        cxn.run(append(secret_key_file, f"SECRET_KEY = '{key}'"))
    cxn.run(append(settings_path, "\nfrom .secret_key import SECRET_KEY"))


def _update_virtualenv(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run(f"{virtualenv_folder}/bin/pip install --upgrade pip")
    cxn.run(f"{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt")


def _update_static_files(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run(f"cd {source_folder} && {virtualenv_folder}/bin/python manage.py collectstatic --noinput")


def _update_database(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run(f"cd {source_folder} && {virtualenv_folder}/bin/python manage.py migrate --noinput")


def _restart_gunicorn_service(cxn: Connection):
    cxn.run("sudo systemctl enable gunicorn", pty=True)
    cxn.run("sudo systemctl start gunicorn", pty=True)
    cxn.run("sudo systemctl restart gunicorn", pty=True)


def _ingest_dictionary(cxn: Connection, source_folder, virtualenv_folder):
    cxn.run(f"cd {source_folder} && {virtualenv_folder}/bin/python manage.py ingest_dictionary")


def sed(filename: str, before: str, after: str) -> str:
    for char in "/'":
        before = before.replace(char, r'\%s' % char)
        after = after.replace(char, r'\%s' % char)
    for char in "()":
        after = after.replace(char, r'\%s' % char)
    return f"sed -i.bak -r 's/{before}/{after}/g' \"{filename}\""


def exists(filename: str) -> str:
    return f"if [ -e {filename} ]; then echo 1; else echo 0; fi"


def append(filename: str, text: str) -> str:
    return f"echo '{text}' >> {filename}"


class DeployException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
