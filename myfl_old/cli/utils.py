import typer

from typing import Iterable, AsyncIterable


def echo(obj):
    if isinstance(obj, str):
        typer.echo(obj)
    elif isinstance(obj, dict):
        typer.echo(obj)
    elif isinstance(obj, Iterable):
        for row in obj:
            typer.echo(row)
    else:
        typer.echo(obj)
