from io import StringIO

class open_line(object):
    """Read ahead by one line. To the client it looks like we know the
    read will succeed before we issue it."""
    def __init__(self,name):
        self.fh = open(name)
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

def example():
    fh = open_line('/etc/hosts')
    count = 1
    while fh.more():
        line = fh.readline()[:-1]
        print ("%3.3s  %s" % (count,line))
        count +=1 
    fh.close()

"""
Consider a file of records described by,

       file := record*
     record := code seperator weight
       code := a..z
  seperator := '|'
     weight := integer

The file is sorted on the code, so that we have batches of weights.
We want to sumerize the weight per batch.
With the problem in mind, a better description of the input file is

           file := batch*
          batch := head-record ; more-record
    head-record := record
    more-record := record*
         record := code seperator weight
           code := a..z
      seperator := '|'
         weight := integer

A file is an iteration of batches and a batch is an iteration records.
A batch must have at least one record, because otherwise we would have no code to recognise it.
"""

batch_data = """a|10
a|20
a|30
b|5
h|1
h|2
"""

def ideal():
    # Parallel structure to the BNF above.
    # fh = b_open(StringIO(batch_data))
    fh = b_open(open("test.dat"))
    while fh.more_batches():
        code,weight = fh.readline()[:-1].split('|') # first rec of batch
        total = int(weight)
        while fh.more_records_in_this_batch(code):
            _,weight = fh.readline()[:-1].split('|')
            total += int(weight)
        print ("%s|%s" % (code,total))
    fh.close()

""" Now we need to invent the class that makes this ideal possible."""

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
      
def dedup():
    # Parallel structure to the BNF above.
    fh = b_open(open("test.dat"))
    while fh.more_batches():
        line = fh.readline()[:-1]
        print (line)
        code,_ = line.split('|')
        while fh.more_records_in_this_batch(code):
            fh.readline()[:-1]
    fh.close()

if __name__ == '__main__': 
   example()
   ideal()
   print ('= ' *10 , 'dedup')
   dedup()
