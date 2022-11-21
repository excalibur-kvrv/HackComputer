from command import Command

class CodeWriter:
  def __init__(self, output_file=None, stream=None):
    if not (output_file or stream):
      raise ValueError("Output file or a write stream must be provided.")
    
    if output_file:
      self.stream = open(output_file, "w")
    else:
      if stream.mode != "w":
        raise ValueError(f"File opened not opened in 'w' mode instead is open in {stream.mode}")
      
      self.stream = stream
  
  def writeArithmetic(self, command: str):
    pass
  
  def writePushPop(self, command: Command, segment: str, index: int):
    pass
  
  def close(self):
    pass