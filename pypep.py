
import re

atomic_symbols = {
  1: "H",
  2: "HE",
  3: "LI",
  4: "BE",
  5: "B",
  6: "C",
  7: "N",
  8: "O",
  9: "F",
  10: "NE",
  11: "NA",
  12: "MG",
  13: "AL",
  14: "SI",
  15: "P",
  16: "S",
  17: "CL",
  18: "AR",
  19: "K",
  20: "CA",
  21: "SC",
  22: "TI",
  23: "V",
  24: "CR",
  25: "MN",
  26: "FE",
  27: "CO",
  28: "NI",
  29: "CU",
  30: "ZN",
  31: "GA",
  32: "GE",
  33: "AS",
  34: "SE",
  35: "BR",
  36: "KR",
  37: "RB",
  38: "SR",
  39: "Y",
  40: "ZR",
  41: "NB",
  42: "MO",
  43: "TC",
  44: "RU",
  45: "RH",
  46: "PD",
  47: "AG",
  48: "CD",
  49: "IN",
  50: "SN",
  51: "SB",
  52: "TE",
  53: "I",
  54: "XE",
  55: "CS",
  56: "BA",
  57: "LA",
  58: "CE",
  59: "PR",
  60: "ND",
  61: "PM",
  62: "SM",
  63: "EU",
  64: "GD",
  65: "TB",
  66: "DY",
  67: "HO",
  68: "ER",
  69: "TM",
  70: "YB",
  71: "LU",
  72: "HF",
  73: "TA",
  74: "W",
  75: "RE",
  76: "OS",
  77: "IR",
  78: "PT",
  79: "AU",
  80: "HG",
  81: "TL",
  82: "PB",
  83: "BI",
  84: "PO",
  85: "AT",
  86: "RN",
  87: "FR",
  88: "RA",
  89: "AC",
  90: "TH",
  91: "PA",
  92: "U",
  93: "NP",
  94: "U6",
  95: "U5",
  96: "U1",
  97: "U2",
  98: "U3",
  99: "U4",
  100: "FM",
  "E": "E",
  "D": "D"
}

def atomic_number(sym, default=None):
  for k,v in atomic_symbols.items():
    if v == sym:
      return k
  return default
  
def atomic_symbol(num, default=None):
  return atomic_symbols.get(num, default)

class Propellant(dict):
  """Propellant data"""
  
  def __init__(self, data=None):
    self["flags"] = None
    self["linenum"] = None
    self["name"] = None
    
    self["elem"] = [None for i in range(6)]
    self["coef"] = [None for i in range(6)]
    
    self["heat"] = None
    self["density"] = None
    
    if data:
      for k,v in data.items():
        if k.startswith("anum_"):
          i = int(k[5:])-1
          self["coef"][i] = v
        elif k.startswith("asym_"):
          i = int(k[5:])-1
          self["elem"][i] = atomic_number(v, 0)
        else:
          self[k] = v
        
  def __repr__(self):
    parts = [
      self["flags"],
      str(self["linenum"]),
      self["name"],
      str(self["coef"][0]) + atomic_symbol(self["elem"][0], ""),
      str(self["coef"][1]) + atomic_symbol(self["elem"][1], ""),
      str(self["coef"][2]) + atomic_symbol(self["elem"][2], ""),
      str(self["coef"][3]) + atomic_symbol(self["elem"][3], ""),
      str(self["coef"][4]) + atomic_symbol(self["elem"][4], ""),
      str(self["coef"][5]) + atomic_symbol(self["elem"][5], ""),
      str(self["heat"]),
      str(self["density"]),
    ]
    return " ".join(parts)

class PropellantList(dict):
  """Load propellant data file"""
  
  fname = None
  re_line = None
  re_cont = None
  
  def __init__(self, filename=None):
    # (A4,I5,A30,6(I3,A2),F5.0,F6.0)
    parts = [
      r'(?P<flags>[a-zA-Z\*\+]{0,4})',
      r'(?P<linenum>[0-9]{1,5})',
      r'(?P<name>.{0,29}\S)',
      
      r'(?P<anum_1>[0-9]{1,3})(?P<asym_1>[a-zA-Z]{0,2})',
      r'(?P<anum_2>[0-9]{1,3})(?P<asym_2>[a-zA-Z]{0,2})',
      r'(?P<anum_3>[0-9]{1,3})(?P<asym_3>[a-zA-Z]{0,2})',
      r'(?P<anum_4>[0-9]{1,3})(?P<asym_4>[a-zA-Z]{0,2})',
      r'(?P<anum_5>[0-9]{1,3})(?P<asym_5>[a-zA-Z]{0,2})',
      r'(?P<anum_6>[0-9]{1,3})(?P<asym_6>[a-zA-Z]{0,2})',
      
      r'(?P<heat>-?[0-9.]{1,6})',
      r'(?P<density>-?[0-9.]{1,6})',
    ]
    self.re_line = re.compile(r'\s+'.join(parts) + r'\s*]?\s*\Z')
    
    parts = [
      r'(?P<flags>\+{1,4})',
      r'(?P<linenum>[0-9]{1,5})',
      r'(?P<name>.{0,29}\S)',
    ]
    self.re_cont = re.compile(r'\s+'.join(parts) + r'\s*]?\s*\Z')
    
    if filename is not None:
      self.load(filename)
      
  def load(self, filename):
    self.fname = filename
    
    fsock = open(filename, 'rb')
    self.__parse(fsock)
    fsock.close
    
  def __parse(self, fsock):
    last_linenum = 0
    for line in fsock:
      # Match line and get dict of results
      re_m = self.re_line.match(line)
      m = None
      
      if re_m:
        m = re_m.groupdict()
        
        m["linenum"] = int(m["linenum"])
        for i in range(1, 7):
          m["anum_" + str(i)] = int(m["anum_" + str(i)])
        m["heat"] = float(m["heat"])
        m["density"] = float(m["density"])
        
        self[m["linenum"]] = Propellant(m)
        last_linenum = m["linenum"]
      else:
        re_m = self.re_cont.match(line)
        if re_m:
          m = re_m.groupdict()
          
          prop = self[last_linenum]
          prop["name"] = m["name"]
          prop["linenum"] = int(m["linenum"])
          self[prop["linenum"]] = prop
          last_linenum = prop["linenum"]
                  
class Thermo(dict):
  """Thermo data"""

  def __init__(self, data=None):
    self["name"] = None
    self["comments"] = None
    self["nint"] = None
    self["id"] = None
    self["elem"] = [None for i in range(5)]
    self["coef"] = [None for i in range(5)]
    self["state"] = None
    self["weight"] = None
    self["heat"] = None
    self["dho"] = None
    self["range"] = [[None for j in range(2)] for i in range(4)]
    self["ncoef"] = [None for i in range(4)]
    self["ex"] = [[None for j in range(8)] for i in range(4)]
    
    self["param"] = [[None for j in range(9)] for i in range(4)]
    
    if data:
      for k,v in data.items():
        self[k] = v

class ThermoList(dict):
  """Load thermo data file"""
  
  fname = None
  re_name = None
  re_formula = None
  re_data = None
  
  def __init__(self, filename=None):
    # Initial format of thermo.dat:
    # interval   variable   type	size	description
    # -----------------------------------------------------------------------------
    # (0, 18)    name	      string	18	compound name
    # (18, 73)   comments   string	55	comment
    # (73, 75)   nint	      int	2	the number of temperature intervals
    # (75, 81)   id	      string	6	the material id
    # 81	   state      int	1	0 - GAS, else CONDENSED
    # (82, 95)   weight     float	13	molecular weight
    # (95, 108)  enth/heat  float	13	enthaply if nint == 0 
    #                                         else heat of formation
    # ...
    # rest of file
    # ...
    parts = [
      r'(?P<name>.{18})',
      r'(?P<comments>.{55})',
    ]
    self.re_name = re.compile(r''.join(parts) + r'\s*\Z')
    
    parts = [
      r'(?P<nint>[0-9\s]{3})',
      r'(?P<id>.{6})',
    ]
    self.re_formula = re.compile(r''.join(parts) + r'\s*\Z')
    
    if filename is not None:
      self.load(filename)
      
  def load(self, filename):
    self.fname = filename
    
    fsock = open(filename, 'rb')
    self.__parse(fsock)
    fsock.close
    
  def __parse(self, fsock):
    last_linenum = 0
    for line in fsock:
      # Match line and get dict of results
      re_m = self.re_line.match(line)
      m = None
      
      if re_m:
        m = re_m.groupdict()
      else:
        re_m = self.re_cont.match(line)
        if re_m:
          m = re_m.groupdict()
          
      if m:
        m["linenum"] = int(m["linenum"])
        
        if m["flags"] == "+":
          name = m["name"]
          linenum = m["linenum"]
          
          m = self[last_linenum]
          
          m["name"] = name
          m["linenum"] = linenum
          
        for i in range(1, 7):
          m["anum_" + str(i)] = int(m["anum_" + str(i)])
          
        m["heat"] = float(m["heat"])
        m["density"] = float(m["density"])
        
        self[m["linenum"]] = Propellant(m)
        last_linenum = int(m["linenum"])
          
if __name__ == '__main__':
  proplist = PropellantList('propellant.dat')
  #print proplist
  
  thermolist = ThermoList('thermo.dat')
  print thermolist
  