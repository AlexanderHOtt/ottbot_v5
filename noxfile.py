import nox
from nox.sessions import Session


@nox.session(reuse_venv=True)
def format_code(session: Session):
    session.install("isort")
    session.install("black")

    session.run("isort", "ottbot")
    session.run("black", "ottbot")


@nox.session(reuse_venv=True)
def lint_code(session: Session):
    session.install("codespell")
    session.install("flake8")
    session.install("-r", "flake8-requirements.txt")

    session.run("codespell", "--ignore-words", ".codespell.ignore", "ottbot")
    session.run("flake8", "ottbot")


@nox.session(reuse_venv=True)
def typecheck_code(session: Session):
    session.install("-r", "requirements.txt", "-r", "type-requirements.txt")
    session.install("mypy")
    session.install("pyright")

    session.run("mypy", "ottbot", "--pretty")
    session.run("pyright", "ottbot")
