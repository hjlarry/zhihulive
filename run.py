import asyncio
import click
from aiohttp import web

from network import crawl
from network import transform
from models import create_table
from web.main import app


@click.group()
def cli():
    pass


@click.command()
def initdb():
    click.echo('Initialized the database and create table')
    create_table()


@click.command()
def dropdb():
    click.echo('Dropped the database')


@click.command()
def crawl():
    click.echo('Start crawl')
    loop = asyncio.get_event_loop()
    crawler = crawl.Crawler(loop=loop)
    loop.run_until_complete(crawler.crawl())
    click.echo('Finished in {:.3f} seconds'.format(crawler.t1 - crawler.t0))


@click.command()
def transform():
    click.echo('Start transform')
    loop = asyncio.get_event_loop()
    transformer = transform.Transformer(loop=loop)
    loop.run_until_complete(transformer.transform())
    click.echo('Finished in {:.3f} seconds'.format(transformer.t1 - transformer.t0))


@click.command()
def webserver():
    click.echo('Start webserver')
    web.run_app(app)


cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(crawl)
cli.add_command(transform)
cli.add_command(webserver)

if __name__ == '__main__':
    cli()
