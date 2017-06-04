# Placeholder program, is not the launcher LOL
# TL;DR: Test program

import click


@click.group()
def cli():
    """
    This is an example text that will be shown in help command.
    Content and short explained text will be added here later.
    """


@cli.command('init', short_help='init the repo')
@click.option('--text', help='custom text to repeat',
              metavar='<text>')
def echo(text):
    """Example command that repeats something if told to do so."""
    if text:
        click.echo(text)
    else:
        click.echo('foo bar')


if __name__ == '__main__':
    echo()
