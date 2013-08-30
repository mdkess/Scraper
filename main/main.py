__author__ = 'mdkess'

import sys
import urllib2
import re
from HTMLParser import HTMLParser


class MyHTMLParser(HTMLParser):
    # Simple regex for matching email addresses
    EMAIL_REGEX = r'(.*[^a-zA-Z0-9\._])?([a-zA-Z0-9\._-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_\.-]+)'
    def __init__(self):
        HTMLParser.__init__(self)
        self.__hrefs = []
        self.__emails = []

    def hrefs(self):
        return self.__hrefs

    def emails(self):
        return self.__emails

    def handle_starttag(self, tag, attrs):
        #print 'handle_starttag:', tag, attrs
        for attr in attrs:
            if attr[0] == 'href':
                self.__hrefs.append(attr[1])

    def handle_endtag(self, tag):
        #print 'handle_endtag:', tag
        pass

    def handle_data(self, data):
        match = re.match(MyHTMLParser.EMAIL_REGEX, data)
        if match is not None:
            print "Found email", match.group(2)
            self.__emails.append(match.group(2))


def main():
    seen_hrefs = {}
    external_hrefs = {}
    site_map = { }

    base = "http://ma.rtin.xxx/"

    hrefs = ['/']

    external_href = '^(http|https|ftp|ftps)://'
    bad_hrefs = ['javascript:void(0)']
    mailto_href = 'mailto:(.*)'

    external_href_pattern = re.compile(external_href)

    max_depth = 100

    count = 0

    header = {'User-Agent': 'Simple web parser by github.com/mdkess - just for fun'}

    while hrefs.__len__() > 0 and count < max_depth:
        parser = MyHTMLParser()
        count += 1

        target = hrefs[0]
        site_map[target] = {
            'internal_links': [],
            'external_links': [],
            'emails': []
        }

        print 'Parsing', target
        request = urllib2.Request(base + target, headers=header)
        hrefs.pop(0)
        html = urllib2.urlopen(request).read()
        parser.feed(html)

        site_map[target]['emails'] = parser.emails()


        for href in parser.hrefs():
            if href.__len__() > 0 and href not in bad_hrefs and href[0] != '#':
                matches = re.match(external_href_pattern, href)
                if matches is None:
                    matches = re.match(mailto_href, href)
                    if matches is None:
                        site_map[target]['internal_links'].append(href)
                        if href not in seen_hrefs:
                            seen_hrefs[href] = True
                            hrefs.append(href)
                    else:
                        if matches.group(1) not in site_map[target]['emails']:
                            site_map[target]['emails'].append(matches.group(1))
                else:
                    site_map[target]['external_links'].append(href)
                    external_hrefs[href] = True
        print parser.emails()
    print site_map

if __name__ == '__main__':
    sys.exit(main())
