# pySML

## Abstract

pySML is a Python 3.5 implementation of the Smart Message Language v1.03 (see
https://de.wikipedia.org/wiki/Smart_Message_Language & http://www.emsycon.de/downloads/SML_081112_103.pdf) using the
Transport Protocol v1.
Primary it is developed to interpret received SML telegrams. But it is also possible to edit received SML telegrams.
Create custom SML telegrams is not yet included.

Based on SML_Telegram pySML provides symbolic access to the messages of a telegram, and their specific sequences,
choices, integers, booleans or octet strings.

## Example

### Print a SML telegram

```python
import pySML
telegram      = pySML.SML_Telegram()
telegram.data = bytearray([
    0x1B,0x1B,0x1B,0x1B,0x01,0x01,0x01,0x01,

    0x76,0x07,0x00,0x14,0x04,0x82,0x17,0x29,0x62,0x00,0x62,0x00,0x72,0x63,0x01,0x01,
    0x76,0x01,0x01,0x07,0x00,0x14,0x01,0xD4,0xB2,0x63,0x09,0x45,0x4D,0x48,0x58,0x58,
    0x58,0x58,0x58,0x01,0x01,0x63,0xAE,0x74,0x00,

    0x76,0x07,0x00,0x14,0x04,0x82,0x17,0x2A,0x62,0x00,0x62,0x00,0x72,0x63,0x07,0x01,
    0x77,0x01,0x09,0x45,0x4D,0x48,0x58,0x58,0x58,0x58,0x58,0x07,0x01,0x00,0x62,0x0A,
    0xFF,0xFF,0x72,0x62,0x01,0x65,0x01,0xD4,0x5C,0x83,0x7B,0x77,0x07,0x81,0x81,0xC7,
    0x82,0x03,0xFF,0x01,0x01,0x01,0x01,0x04,0x45,0x4D,0x48,0x01,0x77,0x07,0x01,0x00,
    0x00,0x00,0x00,0xFF,0x01,0x01,0x01,0x01,0x0F,0x01,0x45,0x4D,0x48,0x30,0x30,0x30,
    0x58,0x58,0x58,0x58,0x58,0x58,0x58,0x01,0x77,0x07,0x01,0x00,0x00,0x00,0x09,0xFF,
    0x01,0x01,0x01,0x01,0x0B,0x09,0x01,0x45,0x4D,0x48,0x00,0x00,0x4F,0x1B,0xDE,0x01,
    0x77,0x07,0x01,0x00,0x01,0x08,0x00,0xFF,0x64,0x00,0x01,0x82,0x01,0x62,0x1E,0x52,
    0xFF,0x56,0x00,0x02,0x2E,0x4A,0xBE,0x01,0x77,0x07,0x01,0x00,0x01,0x08,0x01,0xFF,
    0x01,0x01,0x62,0x1E,0x52,0xFF,0x56,0x00,0x02,0x2E,0x48,0x5B,0x01,0x77,0x07,0x01,
    0x00,0x01,0x08,0x02,0xFF,0x01,0x01,0x62,0x1E,0x52,0xFF,0x56,0x00,0x00,0x00,0x02,
    0x63,0x01,0x77,0x07,0x01,0x00,0x10,0x07,0x00,0xFF,0x01,0x01,0x62,0x1B,0x52,0xFF,
    0x55,0x00,0x00,0x0E,0x6C,0x01,0x77,0x07,0x01,0x00,0x24,0x07,0x00,0xFF,0x01,0x01,
    0x62,0x1B,0x52,0xFF,0x55,0x00,0x00,0x05,0x6C,0x01,0x77,0x07,0x01,0x00,0x38,0x07,
    0x00,0xFF,0x01,0x01,0x62,0x1B,0x52,0xFF,0x55,0x00,0x00,0x07,0x28,0x01,0x77,0x07,
    0x01,0x00,0x4C,0x07,0x00,0xFF,0x01,0x01,0x62,0x1B,0x52,0xFF,0x55,0x00,0x00,0x01,
    0xD8,0x01,0x77,0x07,0x81,0x81,0xC7,0x82,0x05,0xFF,0x01,0x72,0x62,0x01,0x65,0x01,
    0xD4,0x5C,0x83,0x01,0x01,0x83,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x01,0x01,0x63,0xBC,0xD7,0x00,

    0x76,0x07,0x00,0x14,0x04,0x82,0x17,0x2B,0x62,0x00,0x62,0x00,0x72,0x63,0x02,0x01,
    0x71,0x01,0x63,0xB9,0x9D,0x00,0x00,

    0x1B,0x1B,0x1B,0x1B,0x1A,0x01,0x73,0x29
  ])

print(telegram.getText())
```

`telegram = pySML.SML_Telegram()` creates an SML_Telegram object that is filled with received data via
`telegram.data = bytearray([..])`.
`telegram.getText()` returns a itemized human readable representation of SML telegram object `telegram`.
Printing this produces:

```
----------------------------------------------------------------------------------------------------
76                                 ...             (SML_Message)
  07001404821729                   TransactionId   (SML_OctetString)            ???
  6200                             GroupNo         (SML_UnsignedInteger08)      0x0; 0
  6200                             AbortOnError    (SML_UnsignedInteger08)      0x0; 0
  72                               ...             (SML_MessageBody)
    630101                         Tag             (SML_UnsignedInteger16)      0x101; 257
    76                             ...             (SML_PublicOpenRes)          Element
      01                           CodePage        (SML_OctetString)            None
      01                           ClientId        (SML_OctetString)            None
      07001401d4b263               ReqFileId       (SML_OctetString)             ¶☺?c
      09454d485858585858           ServerId        (SML_OctetString)            EMHXXXXX
      01
      01                           SmlVersion      (SML_UnsignedInteger08)      None
  63ae74                           Crc             (SML_UnsignedInteger16)      0xAE74; 44660
  00                               EndOfMessage    (SML_EndOfMessage)           0x0; 0
----------------------------------------------------------------------------------------------------
76                                 ...             (SML_Message)
  0700140482172a                   TransactionId   (SML_OctetString)            ???
  6200                             GroupNo         (SML_UnsignedInteger08)      0x0; 0
  6200                             AbortOnError    (SML_UnsignedInteger08)      0x0; 0
  72                               ...             (SML_MessageBody)
    630701                         Tag             (SML_UnsignedInteger16)      0x701; 1793
    77                             ...             (SML_GetListRes)             Element
      01                           ClientId        (SML_OctetString)            None
      09454d485858585858           ServerId        (SML_OctetString)            EMHXXXXX
      070100620affff               ListName        (SML_OctetString)            ???
      72                           ...             (SML_Time)
        6201                       Tag             (SML_UnsignedInteger08)      0x1; 1
        6501d45c83                 Element         (SML_UnsignedInteger32)      0x1D45C83; 30694531
      7b                           ...             (SML_ListOfValueEntry)       ValList
        77                         ...             (SML_ValueEntry)             [Nr. 0]
          078181c78203             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          01                       Unit            (SML_UnsignedInteger08)      None
          01                       Scaler          (SML_SignedInteger08)        None
          04454d48                                 (SML_OctetString)            EMH
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 1]
          070100000000             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          01                       Unit            (SML_UnsignedInteger08)      None
          01                       Scaler          (SML_SignedInteger08)        None
          0f01454d4830                             (SML_OctetString)            ☺EMH000XXXXXXX
            3030585858
            58585858
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 2]
          070100000009             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          01                       Unit            (SML_UnsignedInteger08)      None
          01                       Scaler          (SML_SignedInteger08)        None
          0b0901454d48                             (SML_OctetString)            ???
            00004f1bde
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 3]
          070100010800             ObjName         (SML_OctetString)            ???
            ff
          64000182                                 (SML_UnsignedInteger)        0x182; 386
          01
          621e                     Unit            (SML_UnsignedInteger08)      0x1E; 30
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          5600022e4abe                             (SML_SignedInteger)          0x22E4ABE; 36588222
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 4]
          070100010801             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621e                     Unit            (SML_UnsignedInteger08)      0x1E; 30
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          5600022e485b                             (SML_SignedInteger)          0x22E485B; 36587611
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 5]
          070100010802             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621e                     Unit            (SML_UnsignedInteger08)      0x1E; 30
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          560000000263                             (SML_SignedInteger)          0x263; 611
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 6]
          070100100700             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621b                     Unit            (SML_UnsignedInteger08)      0x1B; 27
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          5500000e6c                               (SML_SignedInteger32)        0xE6C; 3692
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 7]
          070100240700             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621b                     Unit            (SML_UnsignedInteger08)      0x1B; 27
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          550000056c                               (SML_SignedInteger32)        0x56C; 1388
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 8]
          070100380700             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621b                     Unit            (SML_UnsignedInteger08)      0x1B; 27
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          5500000728                               (SML_SignedInteger32)        0x728; 1832
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 9]
          0701004c0700             ObjName         (SML_OctetString)            ???
            ff
          01
          01
          621b                     Unit            (SML_UnsignedInteger08)      0x1B; 27
          52ff                     Scaler          (SML_SignedInteger08)        0x-1; -1
          55000001d8                               (SML_SignedInteger32)        0x1D8; 472
          01                       ValueSignature  (SML_OctetString)            None
        77                         ...             (SML_ValueEntry)             [Nr. 10]
          078181c78205             ObjName         (SML_OctetString)            ???
            ff
          01
          72                       ...             (SML_Time)
            6201                   Tag             (SML_UnsignedInteger08)      0x1; 1
            6501d45c               Element         (SML_UnsignedInteger32)      0x1D45C83; 30694531
              83
          01                       Unit            (SML_UnsignedInteger08)      None
          01                       Scaler          (SML_SignedInteger08)        None
          830200000000                             (SML_OctetString)
            0000000000
            0000000000
            0000000000
            0000000000
            0000000000
            0000000000
            0000000000
            0000000000
            00000000
          01                       ValueSignature  (SML_OctetString)            None
      01                           ListSignature   (SML_OctetString)            None
      01
  63bcd7                           Crc             (SML_UnsignedInteger16)      0xBCD7; 48343
  00                               EndOfMessage    (SML_EndOfMessage)           0x0; 0
----------------------------------------------------------------------------------------------------
76                                 ...             (SML_Message)
  0700140482172b                   TransactionId   (SML_OctetString)            ???
  6200                             GroupNo         (SML_UnsignedInteger08)      0x0; 0
  6200                             AbortOnError    (SML_UnsignedInteger08)      0x0; 0
  72                               ...             (SML_MessageBody)
    630201                         Tag             (SML_UnsignedInteger16)      0x201; 513
    71                             ...             (SML_PublicCloseRes)         Element
      01                           GlobalSignature (SML_OctetString)            None
  63b99d                           Crc             (SML_UnsignedInteger16)      0xB99D; 47517
  00                               EndOfMessage    (SML_EndOfMessage)           0x0; 0
```

### Print a single SML message from within a SML telegram

```python
import pySML
telegram      = pySML.SML_Telegram()
telegram.data = bytearray([ as above ])

messages      = telegram.getMssg()

print(messages[-1].getText())
```

### Access elements of a received SML telegram

```python
import pySML
telegram      = pySML.SML_Telegram()
telegram.data = bytearray([ as above ])

print("msg 0, ServerId            >> ", telegram.getMssg()[0].MessageBody.Element.ServerId.valu         )
print("msg 1, DeviceClasification >> ", telegram.getMssg()[1].MessageBody.Element.ValList.valu[ 1].Value)
```

### Change values inside an SML telegram

```python
import pySML
telegram      = pySML.SML_Telegram()
telegram.data = bytearray([ as above ])

telegram.getMssg()[0].MessageBody.Element.ServerId.valu = bytearray(b'HelloSML')

print(telegram.getText())
```
