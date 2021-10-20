#!python3

# Simple file upload through SQL queries, using the PostgreSQL large object interface.

import math
import psycopg2
import random
import sys

# ___BEGGINING_OF_CONFIG___
CONFIG_DB_HOST = "127.0.0.1"
CONFIG_DB_PORT = "5432"
CONFIG_DB_DATABASE = "test"
CONFIG_DB_USER = "admin"
CONFIG_DB_PASSWORD = "password"
# ___END_OF_CONFIG___

BLOCK_LENGTH = 2048

print("[.] Starting...")

if len(sys.argv) < 3:
    print(
        "[.] Usage: {scriptName} (local file path) (remote file path)".format(
            scriptName=sys.argv[0]
        )
    )
    exit(0)

loid = random.randint(10000, 100000)
print("[.] Tho choossen LOID is {loid}".format(loid=loid))

localPath = sys.argv[1]
remotePath = sys.argv[2]

print("[.] Loading local file ({localPath})".format(localPath=localPath))
try:
    data = open(localPath, "rb").read()

except Exception as e:
    print("[-] Some errors occurred reading in the local file.")
    print(e)
else:
    print("[+] The local file was successfully loaded.")

try:
    dbConnection = psycopg2.connect(
        host=CONFIG_DB_HOST,
        port=CONFIG_DB_PORT,
        database=CONFIG_DB_DATABASE,
        user=CONFIG_DB_USER,
        password=CONFIG_DB_PASSWORD,
    )
    dbCursor = dbConnection.cursor()
    print("[+] Connected")

    dbCursor.execute("SELECT lo_create({loID});".format(loID=loid))

    print("[.] Starting upload")
    for pageNo in range(math.ceil(len(data) / BLOCK_LENGTH)):
        dbCursor.execute(
            "INSERT INTO pg_largeobject (loid,pageno,data) VALUES ('{loid}','{pageNo}',decode('{hexData}','hex'));".format(
                loid=loid,
                pageNo=pageNo,
                hexData=data[pageNo * BLOCK_LENGTH : (pageNo + 1) * BLOCK_LENGTH].hex(),
            )
        )

    print("[.] Starting export to {exportPath}".format(exportPath=remotePath))
    dbCursor.execute(
        "SELECT lo_export({loid}, '{exportPath}');".format(
            loid=loid, exportPath=remotePath
        )
    )

except Exception as e:
    print("[-] Some errors occurred.")
    print(e)

else:
    print("[+] File uploaded successfully.")

finally:
    dbCursor.close()
    dbConnection.close()
