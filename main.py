from io import StringIO
import argparse

class open_text(object):
    """Read ahead by one line. To the client it looks like we know the
    read will succeed before we issue it."""
    def __init__(self,fh):
        self.fh = fh
        self.buf = self.fh.readline()
    def more(self):
        return self.buf != ''
    def readline(self):
        line = self.buf
        if self.more():
            self.buf = self.fh.readline()
        return line
    def close(self):
        self.fh.close()

def cat(fh0):
    fh = open_text(fh0)
    count = 0
    while fh.more():
        count +=1 
        line = fh.readline()[:-1]
        print ("%3.3s  %s" % (count,line))
    fh.close()

"""
Consider a file of records described by,

       file := record*
     record := code separator weight
       code := a..z
  seperator := '|'
     weight := integer

The file is sorted on the code, so that we have batches of weights. We
want to sumerize the weight per batch.

With this problem in mind, a better description of the input file is

           file := batch*
          batch := head-record ; more-record
    head-record := record
    more-record := record*
         record := code separator weight
           code := a..z
      seperator := '|'
         weight := integer

A file is an iteration of batches and a batch is an iteration records.

A batch must have at least one record, because otherwise we would have
no code to recognise it.
"""

batch_data = """a|10
a|20
a|30
b|5
h|1
h|2
"""

def ideal(fh0):
    # Parallel structure to the BNF above.
    fh = b_open(fh0)
    while fh.more_batches():
        code,weight = fh.readline()[:-1].split('|') # first rec of batch
        total = int(weight)
        while fh.more_records_in_this_batch(code):
            _,weight = fh.readline()[:-1].split('|')
            total += int(weight)
        print ("%s|%s" % (code,total))
    fh.close()

""" Now we need to invent the class that makes this ideal function
possible."""

class b_open(object):
    def __init__(self,fh):
        self.fh = fh
        self.buf = self.fh.readline()
    def more_batches(self):
        return self.buf != ''
    def more_records_in_this_batch(self,code):
        cx = self.buf.split('|')[0]
        return cx == code
    def readline(self):
        line = self.buf
        if self.more_batches():
            self.buf = self.fh.readline()
        return line
    def close(self):
        self.fh.close()
      
def dedup(fh0):
    fh = b_open(fh0)
    while fh.more_batches():
        line = fh.readline()[:-1]
        print (line)
        code,_ = line.split('|')
        while fh.more_records_in_this_batch(code):
            fh.readline()[:-1]    # skip
    fh.close()

def demos(dummy): 
   cat(open('/etc/hosts'))
  
   print ('= ' *10 , 'empty')
   cat(open('empty.dat'))
 
   print ('= ' *10 , 'ideal stringio')
   ideal(StringIO(batch_data))
  
   print ('= ' *10 , 'ideal test.dat')
   ideal(open('test.dat'))
  
   print ('= ' *10 , 'ideal empty.dat')
   ideal(open('empty.dat'))
 
   print ('= ' *10 , 'dedup')
   dedup(open('test.dat'))

if __name__ == '__main__': 
   parser = argparse.ArgumentParser(description='file utilities')
   # parser.add_argument('--demo', action='store_true', help='run built-in demos')
   subparsers = parser.add_subparsers(help='sub-command help')
   
   parser_a = subparsers.add_parser('cat', help='copy file to stdout')
   parser_a.add_argument('path', help='cat help')
   parser_a.set_defaults(func=cat)

   parser_b = subparsers.add_parser('ideal', help='ideal help')
   parser_b.add_argument('path', help='ideal help')
   parser_b.set_defaults(func=ideal)

   parser_c = subparsers.add_parser('dedup', help='dedup help')
   parser_c.add_argument('path', help='path to input file')
   parser_c.set_defaults(func=dedup)

   parser_d = subparsers.add_parser('demo', help='run built-in demos')
   parser_d.set_defaults(func=demos, demo='demo')

   pd = parser.parse_args()
   if 'demo' in pd.__dict__:
       pd.func(demos)
   else:
       pd.func(open(pd.path))
