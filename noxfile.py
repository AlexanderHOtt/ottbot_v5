import nox
from nox.sessions import Session


@nox.session(reuse_venv=True)
def format_code(session: Session):
    session.install("isort", "-U")
    session.install("black", "-U")

    session.run("isort", "ottbot")
    session.run("black", "ottbot")


@nox.session(reuse_venv=True)
def lint_code(session: Session):
    session.install("codespell", "-U")
    session.install("flake8", "-U")
    session.install("-r", "flake8-requirements.txt", "-U")

    session.run("codespell", "--ignore-words", ".codespell.ignore", "ottbot")
    session.run("flake8", "ottbot")


@nox.session(reuse_venv=True)
def typecheck_code(session: Session):
    session.install("-r", "requirements.txt", "-r", "type-requirements.txt", "-U")
    session.install("pyright")

    session.run("pyright", "ottbot")
