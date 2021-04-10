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
                             #hits on multiple types from being added more
                             #than once.
  def csv(self):
    return f'"{self._type}","{self._value}"'
  def get_type(self):
    return self._type
  def get_value(self):
    return self._value
