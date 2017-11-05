# pySML
# Copyright (C) 2017  Hallabalooza
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# <http://www.gnu.org/licenses/>.

########################################################################################################################
########################################################################################################################
########################################################################################################################

import copy
import enum
import inspect
import textwrap

########################################################################################################################
########################################################################################################################
########################################################################################################################

WRITE_COL_WIDTH_BIN   = 35
WRITE_COL_WIDTH_NAME  = 15
WRITE_COL_WIDTH_TYPE  = 30

########################################################################################################################
########################################################################################################################
########################################################################################################################

class SMLException(Exception):
  """
  @brief   SML exception class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Mssg=None):
    """
    @brief   Constructor.
    @param   Mssg   The Exception message.
    """
    self._modl = inspect.stack()[1][0].f_locals["self"].__class__.__module__
    self._clss = inspect.stack()[1][0].f_locals["self"].__class__.__name__
    self._mthd = inspect.stack()[1][0].f_code.co_name
    self._mssg = None
    if   ( Mssg == None ): self._mssg = "{}.{}.{}".format(self._modl, self._clss, self._mthd)
    else                 : self._mssg = "{}.{}.{}: {}".format(self._modl, self._clss, self._mthd, Mssg)

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __str__(self):
    """
    @brief   Prints a nicely string representation.
    """
    return repr(self._mssg)

#-----------------------------------------------------------------------------------------------------------------------

class SMLExceptionChecksum(SMLException):
  pass

########################################################################################################################
########################################################################################################################
########################################################################################################################

class _SML_Type(enum.IntEnum):
  """
  @brief   The SML data type enumeration.
  """

  OctetString     = 0x00
  Boolean         = 0x40
  SignedInteger   = 0x50
  UnsignedInteger = 0x60
  Sequence        = 0x70

########################################################################################################################

class _SML_Base:
  """
  @brief   SML objects base class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Type=None):
    """
    @brief   Constructor.
    @param   Type   The _SML_Type of the class inherited from _SML_Base.
    """
    if ( not isinstance(Type, _SML_Type) ): raise SMLException("Argument 'Type' is not of type '_SML_Type'.")
    self._type = Type
    self._valu = None

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def decodeTl(self, Data):
    """
    @brief   Check and itemize the SML Type-Length-Field at the beginning of a byte data list.
    @param   Data   SML byte data list.
    @return  A list of type and length coded in the SML Type-Length-Field, as well as the index of
             the last byte of the Type-Length-Field in the byte data list.
    """
    if ( not isinstance(Data, bytearray) ): raise SMLException("Argument 'Data' is not of type 'bytearray'.")
    if ( Data[0] != 0x01 ):
      try   : vEofTL = next(i for i,v in enumerate(Data) if (v < 0x80))
      except: raise SMLException("Could not determine an index for EofTL.")
      vTyp = _SML_Type(Data[0] & 0x70)
      vLen = sum([v<<(4*i) for i,v in enumerate(reversed([(j & 0x0F) for j in Data[:(vEofTL+1)]]))])
      if ( (vTyp != _SML_Type.Sequence) and (vLen > len(Data)) ): raise SMLException("TL field encoding is not correct. The TL field length for SML types not equal 'Sequence' shall be included in the TL length information.")
    else:
      vTyp       = None
      vLen       = 0
      vEofTL     = 0
    return [vTyp,vLen,vEofTL]

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def encodeTl(self, Type, Length):
    """
    @brief   Calculate the SML Type-Length-Field suitable for the given parameters.
    @param   Type     The _SML_Type that shall be encoded in the SML Type-Length-Field.
    @param   Length   The length of the payload that shall follow the SML Type-Length-Field.
    @return  A byte data list representing a SML Type-Length-Field.
    """
    if ( not isinstance(Type,   _SML_Type) ): raise SMLException("Argument 'Type' is not of type '_SML_Type'.")
    if ( not isinstance(Length, int      ) ): raise SMLException("Argument 'Length' is not of type 'int'.")
    if ( Length != 0 ):
      if   ( Type != _SML_Type.Sequence ): vLen0 =         vLen1 = Length + (Length.bit_length()+3)//4
      else                               : vLen0 = Length; vLen1 = Length + (Length.bit_length()+3)//4
      vTL = [ (0x80|(vLen0&(0xF<<(n<<2)))>>(n<<2)) for n in reversed(range((vLen1.bit_length()+3)//4)) ]
      vTL[ 0] |= Type
      vTL[-1] &= 0x7F
    else:
      vTL = bytearray([0x01])
    return bytearray(vTL)

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def crc(self, Data, Int=True):
    """
    @brief   Calculate the CRC of a given byte data list.
    @param   Data   SML byte data list.
    @return  The CRC calculated from given byte data list.
    """
    # http://www.photovoltaikforum.com/datenlogger-f5/emh-ehz-protokoll-t86509.html#p836079
    # https://github.com/dailab/libsml/blob/master/sml/src/sml_crc16.c
    if ( not isinstance(Data, bytearray) ): SMLException("Argument 'Data' is not of type 'bytearray'.")
    vTab = [
      0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
      0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
      0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
      0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
      0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
      0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
      0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
      0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
      0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
      0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
      0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
      0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
      0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
      0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
      0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
      0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
      0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
      0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
      0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
      0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
      0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
      0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
      0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
      0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
      0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
      0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
      0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
      0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
      0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
      0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
      0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
      0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78
    ]
    cCrc = 0xFFFF
    for i in range(len(Data)):
      cCrc = (cCrc >> 8) ^ vTab[(cCrc ^ Data[i]) & 0xFF]
    cCrc ^= 0xFFFF
    if   ( True == Int ): return ((cCrc&0xFF)<<8) + ((cCrc&0xFF00)>>8)
    else                : return bytearray([cCrc&0xFF, (cCrc%0xFF00)>>8])

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getText(self, Indent=0, Info=""):
    """
    @brief   Create a human readable representation of all relevant information of a SML object.
    @param   Indent   Number of spaces to indent.
    @param   Info     Extra information to include in human readable representation.
    @return  The human readable representation of a SML object.
    """
    vWrp = textwrap.wrap(self.data.hex(), width=32-Indent, initial_indent=" "*(Indent), subsequent_indent=" "*(Indent+2))
    if   ( isinstance(self._valu, bytearray) ):
      try   : vVal = str(self._valu.decode("utf-8"))
      except: vVal = "???"
    elif ( isinstance(self._valu, int  ) ): vVal = "0x{0:X}; {0:d}".format(self._valu)
    elif ( isinstance(self._valu, bool ) ): vVal = {True:"True", False:"False"}[self._valu]
    else                                  : vVal = str(self._valu)
    vTxt = vWrp[0].ljust(WRITE_COL_WIDTH_BIN) + Info.ljust(WRITE_COL_WIDTH_NAME) + (" (" + self.__class__.__name__ + ")").ljust(WRITE_COL_WIDTH_TYPE) + vVal + "\n" + "\n".join(vWrp[1:])
    return vTxt.rstrip()

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getType(self):
    """
    @brief   Getter method returning the _SML_Type of a SML object.
    @return  The _SML_Type of the SML object.
    """
    return self._type

  def setType(self, Type):
    """
    @brief   Setter method assigning a _SML_Type to a SML object.
    @param   Type   The _SML_Type of the SML object.
    """
    if ( not isinstance(Type, _SML_Type) ): raise SMLException("Argument 'Type' is not of type '_SML_Type'.")
    self._type = Type

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getValu(self):
    """
    @brief   Getter method returning the value of a SML object.
    @return  The value of the SML object.
    """
    return self._valu

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getDataLen(self):
    """
    @brief   Getter method returning the length of the data byte list representation.
    @return  The length of the data byte list representation.
    """
    return len(self.data)

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  type    = property(getType, setType)
  valu    = property(getValu         )
  datalen = property(getDataLen      )

########################################################################################################################
########################################################################################################################
########################################################################################################################

class SML_EndOfMessage(_SML_Base):
  """
  @brief   SML_EndOfMessage class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self):
    """
    @brief   Constructor.
    """
    self._valu = 0x00

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    return bytearray([self._valu])

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation.
    """
    if ( not isinstance(Data, bytearray) ): raise SMLException("Argument 'Data' is not of type 'bytearray'.")
    if ( Data[0] != self._valu           ): raise SMLException("Received 'Data' seems to be no 'EndOfMessage'.")

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  data = property(getData, setData)

########################################################################################################################

class SML_OctetString(_SML_Base):
  """
  @brief   SML_OctetString class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Value=None):
    """
    @brief   Constructor.
    @param   Value   The initial value.
    """
    _SML_Base.__init__(self, _SML_Type.OctetString )
    if ( not (isinstance(Value, type(None)) or isinstance(Value, bytearray)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'bytearray'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setValu(self, Value):
    """
    @brief   Setter method assigning a value directly.
    @param   Value   The value to set.
    """
    if ( not (isinstance(Value, type(None)) or isinstance(Value, bytearray)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'bytearray'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    if ( self._valu == None ): return bytearray([0x01])
    else                     : return self.encodeTl(self.type, len(self._valu)) + self._valu

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation.
    """
    vTyp,vLen,vEofTL = self.decodeTl(Data)
    if ( vTyp == None ):
      self._valu = None
    else:
      if   ( vTyp == _SML_Type.OctetString ): self._valu = bytearray(Data[(vEofTL+1):vLen])
      else                                  : raise SMLException("Received 'Data' seems to be no 'OctetString'.")
      if   ( self.data != Data[:vLen]      ): raise SMLException("Received 'Data' did not match internal representation.")

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  valu = property(_SML_Base.getValu, setValu)
  data = property(          getData, setData)

########################################################################################################################

class SML_Boolean(_SML_Base):
  """
  @brief   SML_Boolean class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Value=None):
    """
    @brief   Constructor.
    @param   Value   The initial value.
    """
    _SML_Base.__init__(self, _SML_Type.Boolean )
    if ( not (isinstance(Value, type(None)) or isinstance(Value, bool)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'bool'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setValu(self, Value):
    """
    @brief   Setter method assigning a value directly.
    @param   Value   The value to set.
    """
    if ( not (isinstance(Value, type(None)) or isinstance(Value, bool)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'bool'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    if ( self._valu == None ): return bytearray([0x01])
    else                     : return self.encodeTl(self._type, 1) + self._valu.to_bytes(1, 'big', signed=False)

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation
    """
    vTyp,vLen,vEofTL = self.decodeTl(Data)
    if ( vTyp == None ):
      self._valu = None
    else:
      if   ( vTyp == _SML_Type.Boolean  ): self._valu = int.from_bytes(Data[(vEofTL+1):vLen], 'big', signed=False )
      else                               : raise SMLException("Received 'Data' seems to be no 'Boolean'.")
      if   ( self.data != Data[:vLen]   ): raise SMLException("Received 'Data' did not match internal representation.")

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  valu = property(_SML_Base.getValu, setValu)
  data = property(          getData, setData)

########################################################################################################################

class SML_Integer(_SML_Base):
  """
  @brief   SML_Integer class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, NBytes=None, Signed=False, Value=None):
    """
    @brief   Constructor.
    @param   NBytes   The number of bytes to determine the range; None means this value will by initially set by 'setData'.
    @param   Signed   Bool value to specifiy whether the SML_Integer is signed or unsigned.
    @param   Value    The initial value.
    """
    _SML_Base.__init__(self, {True:_SML_Type.SignedInteger, False:_SML_Type.UnsignedInteger}[Signed] )
    self._nbytes = NBytes
    if ( (NBytes != None) and (Value != None) ):
      if ( not (isinstance(Value, type(None)) or isinstance(Value, int)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'int'.")
      if ( Value < self.minInteger                                       ): raise SMLException("Argument 'Value' did not match the possible minimum value specified by 'NBytes'.")
      if ( Value > self.maxInteger                                       ): raise SMLException("Argument 'Value' did not match the possible maximum value specified by 'NBytes'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def GetIsSigned(self):
    """
    @brief   Getter method returning whether the SML_Integer is signed or unsigned.
    @return  Boolean value whether the SML_Integer is signed or unsigned.
    """
    if   ( self.type == _SML_Type.SignedInteger   ): return True
    elif ( self.type == _SML_Type.UnsignedInteger ): return False
    else                                           : raise SMLException("Unknown state for 'signed' information.")

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def GetMaxInteger(self):
    """
    @brief   Getter method returning the possible maximum value of a SML_Integer.
    @return  The possible maximum value of a SML_Integer or None if 'NBytes' isn't set yet.
    """
    if   ( self._nbytes != None ): return {True:((2**(self._nbytes*8))//2)-1, False:(2**(self._nbytes*8))}[self.isSigned]
    else                         : return None

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def GetMinInteger(self):
    """
    @brief   Getter method returning the possible minimum value of a SML_Integer.
    @return  The possible minimum value of a SML_Integer or None if 'NBytes' isn't set yet.
    """
    if   ( self._nbytes != None ): return {True:-((2**(self._nbytes*8))//2), False:0}[self.isSigned]
    else                         : return None

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setValu(self, Value):
    """
    @brief   Setter method assigning a value directly.
    @param   Value   The value to set.
    """
    if ( not (isinstance(Value, type(None)) or isinstance(Value, int)) ): raise SMLException("Argument 'Value' is not of type 'None' or 'int'.")
    if ( Value != None and Value < self.minInteger                     ): raise SMLException("Argument 'Value' did not match the possible minimum value specified by 'NBytes'.")
    if ( Value != None and Value > self.maxInteger                     ): raise SMLException("Argument 'Value' did not match the possible maximum value specified by 'NBytes'.")
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    if ( self._valu == None ): return bytearray([0x01])
    else                     : return self.encodeTl(self.type, self._nbytes) + self._valu.to_bytes(self._nbytes, 'big', signed=self.isSigned)

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation
    """
    vTyp,vLen,vEofTL = self.decodeTl(Data)
    if ( vTyp == None ):
      self._valu = None
    else:
      if   ( (self._nbytes != None) and (self._nbytes != (vLen-1)) ): raise SMLException("Received 'Data' length information did not match specified length.") # check if specified _nbytes matches length info in byte data list representation
      else                                                          : self._nbytes = vLen-1 # set _nbytes from byte data list representation
      if   ( vTyp == _SML_Type.SignedInteger   ): self._valu = int.from_bytes(Data[(vEofTL+1):vLen], 'big', signed=True )
      elif ( vTyp == _SML_Type.UnsignedInteger ): self._valu = int.from_bytes(Data[(vEofTL+1):vLen], 'big', signed=False)
      else                                      : raise SMLException("Unknown state for 'signed' information.")
      if ( self.data != Data[:vLen]            ): raise SMLException("Received 'Data' did not match internal representation.")

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  isSigned   = property(GetIsSigned               )
  maxInteger = property(GetMaxInteger             )
  minInteger = property(GetMinInteger             )
  valu       = property(_SML_Base.getValu, setValu)
  data       = property(          getData, setData)

#-----------------------------------------------------------------------------------------------------------------------

class SML_SignedInteger(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=None, Signed=True, Value=Value)

class SML_SignedInteger08(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=1, Signed=True, Value=Value)

class SML_SignedInteger16(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=2, Signed=True, Value=Value)

class SML_SignedInteger32(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=4, Signed=True, Value=Value)

class SML_SignedInteger64(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=8, Signed=True, Value=Value)

class SML_UnsignedInteger(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=None, Signed=False, Value=Value)

class SML_UnsignedInteger08(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=1, Signed=False, Value=Value)

class SML_UnsignedInteger16(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=2, Signed=False, Value=Value)

class SML_UnsignedInteger32(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=4, Signed=False, Value=Value)

class SML_UnsignedInteger64(SML_Integer):
  def __init__(self, Value=0): SML_Integer.__init__(self, NBytes=8, Signed=False, Value=Value)

########################################################################################################################
########################################################################################################################
########################################################################################################################

class SML_Choice(_SML_Base):
  """
  @brief   SML_Choice class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Parent, *args):
    """
    @brief   Constructor.
    @param   Parent   The parent including this SML_Choice.
    @param            SML object representing a explicit choices tag.
    @param            Dictionary of tag values mapping to SML objects.
    """
    _SML_Base.__init__(self, _SML_Type.Sequence )
    if ( not ( len(args) == 0 or len(args) == 2 ) ): raise SMLException("Number of arguments is wrong.")
    self._typ = "implicit"
    self._tag = None
    self._map = None
    self._par = Parent
    if ( len(args) == 2 ):
      self._typ = "explicit"
      self._tag = args[0]
      self._map = args[1]
      if ( not ( isinstance(self._tag, SML_UnsignedInteger08) or isinstance(self._tag, SML_UnsignedInteger16) ) ): raise SMLException("Argument '2 (Tag)' is not of type 'SML_UnsignedInteger08' or 'SML_UnsignedInteger16'.")
      if ( not isinstance(self._map, dict) ): raise SMLException("Argument '3 (Map)' is not of type 'dict'.")
      for k,v in self._map.items():
        if ( not isinstance(k, int)   ): raise SMLException("Key '{}' of argument '3 (Map)' of type 'dict' is not of type 'int'.".format(k))
        if ( k < self._tag.minInteger ): raise SMLException("Key '{}' of argument '3 (Map)' of type 'dict' did not match the possible minimum value specified by argument '2 (Tag)'.".format(k))
        if ( k > self._tag.maxInteger ): raise SMLException("Key '{}' of argument '3 (Map)' of type 'dict' did not match the possible maximum value specified by argument '2 (Tag)'.".format(k))
        if ( not ( isinstance(v, SML_OctetString) or
                   isinstance(v, SML_Boolean)     or
                   isinstance(v, SML_Integer)     or
                   isinstance(v, SML_SignedInteger08  ) or isinstance(v, SML_SignedInteger16  ) or isinstance(v, SML_SignedInteger32  ) or isinstance(v, SML_SignedInteger64  ) or
                   isinstance(v, SML_UnsignedInteger08) or isinstance(v, SML_UnsignedInteger16) or isinstance(v, SML_UnsignedInteger32) or isinstance(v, SML_UnsignedInteger64) or
                   isinstance(v, SML_Sequence)
                 )
           ):
          raise SMLException("Value '{}' of key '{}' of argument '3 (Map)' of type 'dict' is not a valid SML type.".format(v,k))
    self._valu = None
    setattr(Parent, "Element", self._valu)

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getText(self, Indent=0, Info=""):
    """
    @brief   Create a human readable representation of all relevant information of a SML_Sequence.
    @param   Indent   Number of spaces to indent.
    @param   Info     Extra information to include in human readable representation.
    @return  The human readable representation of a SML object.
    """
    if ( self._valu == None ):
      vTxt = (" "*Indent + "01").ljust(WRITE_COL_WIDTH_BIN)
    else:
      if ( self._typ == "implicit" ):
        vTxt = self._valu.getText(Indent=Indent)
      else:
        vTxt = (" "*Indent + self.encodeTl(self.type, 2).hex()).ljust(WRITE_COL_WIDTH_BIN) + "...".ljust(WRITE_COL_WIDTH_NAME) + (" (" + self.__class__.__name__ + ")").ljust(WRITE_COL_WIDTH_TYPE)
        vTxt = vTxt + "\n" + self._tag.getText(Indent=Indent+2, Info="Tag")
        vTxt = vTxt + "\n" + self._valu.getText(Indent=Indent+2, Info="Element")
    return vTxt

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    if ( self._valu == None ):
      return bytearray([0x01])
    else:
      if ( self._typ == "implicit" ):
        return self._valu.data # ???
      else:
        return self.encodeTl(self.type, 2) + self._tag.data + self._valu.data

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation
    """
    if ( not isinstance(Data, bytearray) ): raise SMLException("Argument 'Data' is not of type 'bytearray'.")
    vTyp,vLen,vEofTL = self.decodeTl(Data)
    if ( vTyp == None ):
      self._valu = None
    else:
      if ( self._typ == "implicit" ):
        if   ( vTyp == _SML_Type.OctetString     ): self._valu = SML_OctetString()
        elif ( vTyp == _SML_Type.Boolean         ): self._valu = SML_Boolean()
        elif ( vTyp == _SML_Type.SignedInteger   ):
          if   ( vLen == 2 ): self._valu = SML_SignedInteger08()
          elif ( vLen == 3 ): self._valu = SML_SignedInteger16()
          elif ( vLen == 5 ): self._valu = SML_SignedInteger32()
          elif ( vLen == 9 ): self._valu = SML_SignedInteger64()
          else              : self._valu = SML_SignedInteger()
        elif ( vTyp == _SML_Type.UnsignedInteger ):
          if   ( vLen == 2 ): self._valu = SML_UnignedInteger08()
          elif ( vLen == 3 ): self._valu = SML_UnsignedInteger16()
          elif ( vLen == 5 ): self._valu = SML_UnsignedInteger32()
          elif ( vLen == 9 ): self._valu = SML_UnsignedInteger64()
          else              : self._valu = SML_UnsignedInteger()
        elif ( vTyp == _SML_Type.Sequence        ): self._valu = SML_Sequence()
        self._valu.data = Data
      else:
        Data = Data[(vEofTL+1):]
        self._tag.data  = Data
        Data = Data[self._tag.datalen:]
        self._valu      = self._map[self._tag.valu]
        self._valu.data = Data
        Data = Data[self._valu.datalen:]
    setattr(self._par, "Element", self._valu)

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getValu(self):
    """
    @brief   Override getter method raising AttributeError.
    """
    raise AttributeError

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  data = property(getData, setData)
  valu = property(getValu)

#-----------------------------------------------------------------------------------------------------------------------

class SML_Time(SML_Choice):
  def __init__(self):
    SML_Choice.__init__(self, self, SML_UnsignedInteger08(), {0x01:SML_UnsignedInteger32(),
                                                              0x02:SML_UnsignedInteger32()
                                                             }
                       )

class SML_Status(SML_Choice):
  def __init__(self):
    SML_Choice.__init__(self, self)

class SML_Value(SML_Choice):
  def __init__(self):
    SML_Choice.__init__(self, self)

class SML_MessageBody(SML_Choice):
  def __init__(self):
    SML_Choice.__init__(self, self, SML_UnsignedInteger16(), {0x00000100: SML_PublicOpenReq(),
                                                              0x00000101: SML_PublicOpenRes(),
                                                              0x00000200: SML_PublicCloseReq(),
                                                              0x00000201: SML_PublicCloseRes(),
                                                            #0x00000300: SML_GetProfilePackReq
                                                            #0x00000301: SML_GetProfilePackRes
                                                            #0x00000400: SML_GetProfileListReq
                                                            #0x00000401: SML_GetProfileListRes
                                                            #0x00000500: SML_GetProcParameterReq
                                                            #0x00000501: SML_GetProcParameterRes
                                                            #0x00000600: SML_SetProcParameterReq
                                                            #0x00000601: SML_SetProcParameterRes
                                                              0x00000700: SML_GetListReq(),
                                                              0x00000701: SML_GetListRes()
                                                            #0x0000FF01: SML_AttentionRes
                                                           }
                       )

########################################################################################################################
########################################################################################################################
########################################################################################################################

class SML_Sequence(_SML_Base):
  """
  @brief   SML_Sequence class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, Parent, Elements=None):
    """
    @brief   Constructor.
    @param   Parent     The parent including this SML_Choice.
    @param   Elements   A list of tuples (name, SML object) representing the elements of this SML_Sequence or
                        a single SML object to represent the elements of an 'List Of' SML_Sequence.
    """
    _SML_Base.__init__(self, _SML_Type.Sequence )
    if ( isinstance(Elements, list) ):
      self._name = []
      self._valu = []
      for e in Elements:
        if ( not isinstance(e, tuple)  ): raise SMLException("Element '{}' of argument 'Elements' is not a 'tuple'.".format(e))
        if ( len(e) != 2               ): raise SMLException("Tuple '{}' of argument 'Elements' did not contain 2 elements.".format(e))
        if ( not isinstance(e[0], str) ): raise SMLException("First element of tuple '{}' of argument 'Elements' is not of type 'str'.".format(e))
        vName = e[0]
        vInst = e[1]
        if ( vName not in self._name ):
          self._name.append(vName)
          self._valu.append(vInst)
          setattr(Parent, vName, self._valu[len(self._valu)-1])
        else:
          raise SMLException("First element of tuple '{}' of argument 'Elements' is a duplicate.".format(e))
    else:
      self._name = None
      self._valu = []
      self._objc = Elements

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getText(self, Indent=0, Info=""):
    """
    @brief   Create a human readable representation of all relevant information of a SML_Sequence.
    @param   Indent   Number of spaces to indent.
    @param   Info     Extra information to include in human readable representation.
    @return  The human readable representation of a SML object.
    """
    vTxt = (" "*Indent + self.encodeTl(self.type, len(self._valu)).hex()).ljust(WRITE_COL_WIDTH_BIN) + "...".ljust(WRITE_COL_WIDTH_NAME) + (" (" + self.__class__.__name__ + ")").ljust(WRITE_COL_WIDTH_TYPE) + Info
    if ( self._name != None ):
      for n,o in zip(self._name, self._valu):
        vTxt = vTxt + "\n" + o.getText(Indent+2, n)
    else:
      for i,e in enumerate(self._valu):
        vTxt = vTxt + "\n" + e.getText(Indent=Indent+2, Info="[Nr. {}]".format(i))
    return vTxt

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setValu(self, Value):
    """
    @brief   Setter method assigning a list of values directly to a 'List Of' SML_Sequence.
    @param   Value   The list of values to set.
    """
    if ( self._name != None          ): raise SMLException("This is not a 'List Of' SML_Sequence or there was already data written.")
    if ( not isinstance(Value, list) ): raise SMLException("Argument 'Value' is not of type 'list'.")
    for e in Value:
      if ( not isinstance(e, type(self._objc)) ): raise SMLException("Element '{}' of argument 'Value' is not of type '{}' as configured by the contructor.".format(e, type(self._objc)))
    self._valu = Value

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    return self.encodeTl(self.type, len(self._valu)) + bytearray([b for e in self._valu for b in e.data])

  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation
    """
    if ( not isinstance(Data, bytearray) ): raise SMLException("Argument 'Data' is not of type 'bytearray'.")
    vTyp,vLen,vEofTL = self.decodeTl(Data)
    Data = Data[(vEofTL+1):]
    if ( vTyp == None ):
      self._valu = None
    else:
      if ( self._name != None ):
        for e in self._valu:
          if ( e != None ):
            e.data = Data
            Data = Data[e.datalen:]
      else:
        for e in range(vLen):
          self._objc.data = Data
          Data = Data[self._objc.datalen:]
          self._valu.append( copy.deepcopy(self._objc) )

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  data = property(getData, setData)

#-----------------------------------------------------------------------------------------------------------------------

class SML_ObjReqEntry(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("CodePage",   SML_OctetString()      ),
                                        ("ClientId",   SML_OctetString()      ),
                                        ("ReqFileId",  SML_OctetString()      ),
                                        ("ServerId",   SML_OctetString()      ),
                                        ("Username",   SML_OctetString()      ),
                                        ("Password",   SML_OctetString()      ),
                                        ("SmlVersion", SML_UnsignedInteger08())
                                      ]
                         )

class SML_ValueEntry(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("ObjName",        SML_OctetString()      ),
                                        ("Status",         SML_Status()           ),
                                        ("ValTime",        SML_Time()             ),
                                        ("Unit",           SML_UnsignedInteger08()),
                                        ("Scaler",         SML_SignedInteger08()  ),
                                        ("Value",          SML_Value()            ),
                                        ("ValueSignature", SML_OctetString()      )
                                      ]
                         )

class SML_ListOfValueEntry(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, SML_ValueEntry()
                         )

class SML_PublicOpenReq(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("CodePage",   SML_OctetString()      ),
                                        ("ClientId",   SML_OctetString()      ),
                                        ("ReqFileId",  SML_OctetString()      ),
                                        ("ServerId",   SML_OctetString()      ),
                                        ("Username",   SML_OctetString()      ),
                                        ("Password",   SML_OctetString()      ),
                                        ("SmlVersion", SML_UnsignedInteger08())
                                      ]
                         )

class SML_PublicOpenRes(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("CodePage",   SML_OctetString()      ),
                                        ("ClientId",   SML_OctetString()      ),
                                        ("ReqFileId",  SML_OctetString()      ),
                                        ("ServerId",   SML_OctetString()      ),
                                        ("RefTime",    SML_Time()             ),
                                        ("SmlVersion", SML_UnsignedInteger08())
                                      ]
                         )

class SML_PublicCloseReq(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("GlobalSignature", SML_OctetString())
                                      ]
                         )

class SML_PublicCloseRes(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("GlobalSignature", SML_OctetString())
                                      ]
                         )

#class SML_GetProfilePackReq(SML_Sequence):
#  def __init__(self):
#    SML_Sequence.__init__(self, self, [ ("ServerId",          SML_OctetString()),
#                                        ("Username",          SML_OctetString()),
#                                        ("Password",          SML_OctetString()),
#                                        ("WithRawdata",       SML_Boolean()    ),
#                                        ("BeginTime",         SML_Time()       ),
#                                        ("EndTime",           SML_Time()       ),
#                                        ("ParameterTreePath", SML_TreePath()   ),
#                                        ("ParameterTreePath", SML_TreePath()   ),
#                                      ]
#                         )

class SML_GetListReq(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("ClientId", SML_OctetString()),
                                        ("ServerId", SML_OctetString()),
                                        ("Username", SML_OctetString()),
                                        ("Password", SML_OctetString()),
                                        ("ListName", SML_OctetString())
                                      ]
                         )

class SML_GetListRes(SML_Sequence):
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("ClientId",       SML_OctetString()),
                                        ("ServerId",       SML_OctetString()),
                                        ("ListName",       SML_OctetString()),
                                        ("ActSensorTime",  SML_Time()       ),
                                        ("ValList",        SML_ListOfValueEntry()),
                                        ("ListSignature",  SML_OctetString()),
                                        ("ActGatewayTime", SML_Time()       )
                                      ]
                         )

class SML_Message(SML_Sequence):

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self):
    SML_Sequence.__init__(self, self, [ ("TransactionId", SML_OctetString()),
                                        ("GroupNo",       SML_UnsignedInteger08()),
                                        ("AbortOnError",  SML_UnsignedInteger08()),
                                        ("MessageBody",   SML_MessageBody()),
                                        ("Crc",           SML_UnsignedInteger16()),
                                        ("EndOfMessage",  SML_EndOfMessage())
                                      ]
                         )

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setData(self, Data):
    SML_Sequence.setData(self, Data)
    crc_cmp = self.crc(Data[:(self.datalen-4)])
    crc_dat = self.Crc.valu
    if ( crc_dat != crc_cmp ): raise SMLExceptionChecksum("actual - 0x{:04X}; nominal - 0x{:04X}".format(crc_dat, crc_cmp))

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  data = property(SML_Sequence.getData, setData)

########################################################################################################################
########################################################################################################################
########################################################################################################################

class SML_Telegram(_SML_Base):
  """
  @brief   SML_Telegram class.
  """

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self):
    """
    @brief  Constructor.
    """
    self.__mssg = []

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getText(self):
    vTxt = ""
    for msg in self.__mssg:
      vTxt = vTxt + "-"*100 + "\n"
      vTxt = vTxt + msg.getText().encode("ascii", "replace").decode("ascii") + "\n"
    return vTxt

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getData(self):
    """
    @brief   Getter method returning the data byte list representation.
    @return  The data byte list representation.
    """
    tmp = bytearray([0x1B, 0x1B, 0x1B, 0x1B, 0x01, 0x01, 0x01, 0x01])
    for msg in self.__mssg:
      tmp = tmp + msg.getData()
    lna = len(tmp)%4
    tmp = tmp + bytearray([0x00]*(lna))
    tmp = tmp + bytearray([0x1B, 0x1B, 0x1B, 0x1B, 0x1A, lna])
    tmp = tmp + bytearray(self.crc(tmp, Int=False))
    return tmp

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def setData(self, Data):
    """
    @brief   Setter method assigning a value from a data byte list representation.
    @param   Data   SML byte data list representation.
    """
    if ( Data[:8]    != bytearray([0x1B, 0x1B, 0x1B, 0x1B, 0x01, 0x01, 0x01, 0x01]) ): raise SMLException("Could not find escape sequence 'start of telegram'.")
    if ( Data[-8:-3] != bytearray([0x1B, 0x1B, 0x1B, 0x1B, 0x1A]                  ) ): raise SMLException("Could not find escape sequence 'end of telegram'.")
    if ( Data[-3] not in [0x00, 0x01, 0x02, 0x03]                                   ): raise SMLException("Escape sequence 'end of telegram' contains illegal number of padding bytes.")
    crc_cmp = self.crc(bytearray(Data[:-2]), Int=False)
    crc_dat = Data[-2:]
    if ( crc_dat != crc_cmp                                                         ): raise SMLExceptionChecksum("actual - 0x{}; nominal - 0x{}".format(''.join('{:02X}'.format(x) for x in crc_dat), ''.join('{:02X}'.format(x) for x in crc_cmp)))
    Data = Data[8:(-8-Data[-3])]
    while ( len(Data) > 0 ):
      self.__mssg.append(SML_Message())
      self.__mssg[-1].data = Data
      Data = Data[self.__mssg[-1].datalen:]

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def getMssg(self):
    """
    @brief   Getter method returning the list of SML_Messages in SML_Telegram.
    @return  The list of SML_Messages in SML_Telegram.
    """
    return self.__mssg

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  data = property(getData, setData)
  msg  = property(getMssg)

########################################################################################################################
########################################################################################################################
########################################################################################################################

if ( __name__ == '__main__' ):
  pass
