#every word scraped from a document is stored as a nugget, using this class
#self._type and self._value are the main parts.  An example would be:
#
#self._value = 123.123.123.123
#self._type = IPV4

class nugget:
  def __init__(self, typ, val):
    self._type = typ
    self._value = val
  def __repr__self(self):
    return(f"{self._type} {self._value}")
  def __str__(self):
    return(f"{self._type} {self._value}")
  def __lt__ (self, other):
    return self._value < other._value
  def __gt__ (self, other):
    return other.__lt__(self)
  def __eq__(self, other):
    return hash(self._value) == hash(self._value)
  def __ne__ (self, other):
    return not self.__eq__(other)
  def __hash__(self):
    return hash(self._value) #doing it this way cuts down on one value which
                             #hits on multiple types (e.g. jabber handles versus
                             #twitter handles, which both share format of
                             #@some-annoying-name) from being added more
                             #than once.  Its greedy, if @some-annoying-name is
                             #tagged as a jabber id, then seen as a twitter id,
                             #the titter tag is not created.  Neo4j gets
                             #incomprehensible when I try other solutions...
  def csv(self):
    return f'"{self._type}","{self._value}"'
  def get_type(self):
    return self._type
  def get_value(self):
    return self._value
