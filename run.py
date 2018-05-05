import asyncio

from crawl.crawl import Crawler

loop = asyncio.get_event_loop()
crawler = Crawler(loop=loop)
loop.run_until_complete(crawler.crawl())
print('Finished in {:.3f} seconds'.format(crawler.t1 - crawler.t0))


