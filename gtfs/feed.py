from codecs import iterdecode
from collections import namedtuple
from zipfile import ZipFile
import os
import csv

def _row_stripper(row):
    return (cell.strip() for cell in row)

class CSV(object):
    """A CSV file."""

    def __init__(self, header, rows, feedtype='CSVTuple'):
        self.header = header
        self.Tuple = namedtuple(feedtype, header)
        self.rows = rows
        self.peek_queue = []

    def __repr__(self):
        return '<CSV %s>' % self.header

    def __iter__(self):
        return self

    def _next(self):
        return self.Tuple._make(self.rows.next())

    def next(self):
        if self.peek_queue:
            return self.peek_queue.pop(0)
        return self._next()

    def peek(self):
        self.peek_queue.append(self._next())
        return self.peek_queue[-1]

class Feed(object):
    """A collection of CSV files with headers, either zipped into an archive
    or loose in a folder."""

    def __init__(self, filename, strip_fields=True):
        self.filename = filename 
        self.feed_name = os.path.basename(filename.rstrip('/'))
        self.zf = None
        self.strip_fields = strip_fields
        if not os.path.isdir(filename):
            self.zf = ZipFile(filename)
    
    def __repr__(self):
        return '<Feed %s>' % self.filename

    def unicode_csv_reader(self, file_handle, encoding='utf-8'):
        if encoding == 'utf-8':
            encoding_sig = 'utf-8-sig'
        reader = csv.reader([x.encode(encoding) for x in iterdecode(file_handle, encoding_sig)])
        for row in reader:
            yield [unicode(x, encoding) for x in row]
        return

    def reader(self, filename, encoding='utf-8'):
        if self.zf:
            try:
                file_handle = self.zf.read(filename).split('\n')
            except IOError:
                raise IOError('%s is not present in feed' % filename)
        else:
            file_handle = open(os.path.join(self.filename, filename))
        return self.unicode_csv_reader(file_handle, encoding)

    def read_table(self, filename):
        if self.strip_fields:
            rows = (_row_stripper(row) for row in self.reader(filename))
        else:
            rows = self.reader(filename)
        feedtype = filename.rsplit('/')[-1].rsplit('.')[0].title().replace('_', '')
        return CSV(feedtype=feedtype, header=rows.next(), rows=rows)
