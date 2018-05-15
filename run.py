import asyncio

from network import crawl

loop = asyncio.get_event_loop()
crawler = crawl.Crawler(loop=loop)
loop.run_until_complete(crawler.crawl())
print('Finished in {:.3f} seconds'.format(crawler.t1 - crawler.t0))
# loop = asyncio.get_event_loop()
# t = transform.Transformer(loop=loop)
# loop.run_until_complete(t.get_token())
# print(t.token)
