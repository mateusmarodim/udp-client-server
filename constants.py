DEFAULT_SERVER_PORT = 8080
DEFAULT_CLIENT_PORT = 2024

BUFF_SIZE = 4096

## Formats for struct module
# H - unsigned short
# 4s - 4 byte string
SOURCE_PORT_FORMAT = "H"
DESTINATION_PORT_FORMAT = "H"
LENGTH_FORMAT = "H"
CHECKSUM_FORMAT = "I"
METHOD_FORMAT = "4s"

GET_METHOD = "GET"
LIST_METHOD = "LIST"

## Response codes
RESPONSE_CHUNK = 100
RESPONSE_OK = 200
RESPONSE_NOT_FOUND = 404
RESPONSE_ERROR = 500

"""
UDP Header Format (adapted checksum to support 32bit crc32)
0       7 8     15 16    23 24     31
+--------+--------+--------+--------+
|     Source      |   Destination   |
|      Port       |      Port       |
+--------+--------+--------+--------+
|                 |                 |
|     Length      |    Checksum     |
+--------+--------+--------+--------+
|                 |                 |
|    Checksum     |   data octets   |
+--------+--------+--------+--------+
|
|          data octets ...
+---------------- ...
"""