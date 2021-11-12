// Mysql - MariaDB User-Defined Functions for system calls

// gcc -shared -lc -fPIC -o call_system.so call_system.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_LENGTH (8192)

enum Item_result
{
    STRING_RESULT,
    REAL_RESULT,
    INT_RESULT,
    ROW_RESULT
};

typedef struct st_udf_args
{
    unsigned int arg_count;
    enum Item_result *arg_type;
    char **args;
    unsigned long *lengths;
    char *maybe_null;
} UDF_ARGS;

typedef struct st_udf_init
{
    char maybe_null;
    unsigned int decimals;
    unsigned long max_length;
    char *ptr;
    char const_item;
} UDF_INIT;

char *buffer = NULL;
char *call_system(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error)
{
    if (args->arg_count != 1)
        return (0);

    FILE *fp;
    if ((fp = popen(args->args[0], "r")) == NULL)
        return (0);

    if ((buffer = calloc(BUFFER_LENGTH, sizeof(char))) == NULL)
        return (0);

    char readinBuffer[512];
    int remainingLen = BUFFER_LENGTH;
    while (fgets(readinBuffer, sizeof(readinBuffer), fp) && remainingLen > 0)
    {
        int readinBufferLen = strlen(readinBuffer);
        strncat(
            buffer,
            readinBuffer,
            (remainingLen > readinBufferLen ? remainingLen : readinBufferLen));
        remainingLen -= readinBufferLen;
    }

    return buffer;
}

char call_system_init(UDF_INIT *initid, UDF_ARGS *args, char *message)
{
    free(buffer);
    return (0);
}