from __future__ import division, absolute_import, print_function, unicode_literals

import os
import io
import csv

from codecs import iterdecode
from collections import namedtuple
from zipfile import ZipFile

import six

def _row_stripper(row):
    return (cell.strip() for cell in row)

class CSV(object):
    """A CSV file."""

    def __init__(self, rows, feedtype='CSVTuple'):
        self.header = six.next(rows)
        self.Tuple = namedtuple(feedtype, self.header)
        self.rows = rows

    def __repr__(self):
        return '<CSV %s>' % self.header

    def __iter__(self):
        return self

    def __next__(self):
        return self.Tuple._make(six.next(self.rows))
    next = __next__  # python 2 compatible


class Feed(object):
    """A collection of CSV files with headers, either zipped into an archive
    or loose in a folder."""

    def __init__(self, filename, strip_fields=True):
        self.filename = filename 
        self.feed_name = derive_feed_name(filename)
        self.zf = None
        self.strip_fields = strip_fields
        if not os.path.isdir(filename):
            self.zf = ZipFile(filename)
        if six.PY2:
            self.csv_reader = self.unicode_csv_reader
        else:
            self.csv_reader = csv.reader
    
    def __repr__(self):
        return '<Feed %s>' % self.filename

    def unicode_csv_reader(self, file_handle):
        reader = csv.reader((x.encode('utf-8') for x in iterdecode(file_handle,'utf-8-sig')))
        for row in reader:
            yield [six.text_type(x, 'utf-8') for x in row]
        return

    def reader(self, filename):
        if self.zf:
            try:
                file_handle = io.TextIOWrapper(self.zf.open(filename, 'rU'))
            except IOError:
                raise IOError('%s is not present in feed' % filename)
        else:
            file_handle = open(os.path.join(self.filename, filename))
        return self.csv_reader(file_handle)

    def read_table(self, filename):
        if self.strip_fields:
            rows = (_row_stripper(row) for row in self.reader(filename))
        else:
            rows = self.reader(filename)
        feedtype = filename.rsplit('/')[-1].rsplit('.')[0].title().replace('_', '')
        return CSV(feedtype=feedtype, rows=rows)


def derive_feed_name(filename):
    return os.path.basename(filename.rstrip('/'))
