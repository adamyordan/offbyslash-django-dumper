import argparse
import os
import crawler

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dump django website affected by nginx off-by-slash misconfiguration')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='target url')
    group.add_argument('--file', help='file containing target urls')

    args = parser.parse_args()

    if args.url:
        crawler.Crawler.crawl(args.url)

    else:
        if not os.path.exists(args.file):
            print 'File not found: {}'.format(args.file)
            exit(1)

        targets = open(args.file).read().split('\n')
        for target in targets[:]:
            crawler.Crawler.crawl(target)
