import time
import os
from py2neo import Graph, Node, Relationship #pip install py2neo

class n4j:
  def __init__(self, snarf_class, verbosity):
    self.graph = Graph()
    self.snarf_class = snarf_class
    self.verbose = verbosity
  
  #this function pushes the data in memory into neo4j for visualization
  def store(self):
    for fpath in self.snarf_class.doc2nug.keys():
      if self.check_file(fpath):
        return
      if len(self.snarf_class.doc2nug[fpath]) > 0:
        at = Node("File", path=fpath, name=os.path.basename(fpath))
        tx = self.graph.begin()
        tx.create(at)
        tx.commit()
        if self.verbose:
          print(f"stored file {fpath} in neo4j")
        for nugget in self.snarf_class.doc2nug[fpath]:
          tx = self.graph.begin()
          if self.check_nug(nugget):
            rel = Relationship(at, "CONTAINS", self.graph.nodes.match(nugget.get_type(), letters=nugget.get_value()).first())
            tx.create(rel)
          else:
            new_nugget = Node(nugget.get_type(), letters=nugget.get_value())
            tx.create(new_nugget)
            rel = Relationship(at, "CONTAINS", new_nugget)
            tx.create(rel)
          tx.commit()
          if self.verbose:
            print(f"  added {nugget} to {fpath}")
  
  #this checks to see if a file is already represented in the database instance
  def check_file(self, fpath):
    return self.graph.nodes.match("File", path=fpath).exists()
    
  #this checks to see if a "nugget" is already represented
  def check_nug(self, nugget):
    return self.graph.nodes.match(nugget.get_type(), letters=nugget.get_value()).exists()
        
