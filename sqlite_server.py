import os
from subprocess import Popen, PIPE, STDOUT

def _run_query(query_str):
    global g_attach_query
    query_str = g_attach_query + query_str + ";"
    open("sqlite_server_IN", "wa").write(query_str);
    return open("sqlite_server_OUT", "r").read()

def load(filename, dbname):
    global g_attach_query
    if not os.path.isfile(filename):
        raise Exception("Database %s does not exists." % repr(filename))
    g_attach_query = "attach '%s' as '%s';" % (filename, dbname)

def _sqlite_escape(s):
    return s.replace("'", "''")

def query(query_str, *rest):
    # replace ? with escaped version of arguments
    last = 0
    for obj in rest:
        i = query_str.find("?", last)
        if i == -1:
            raise Exception("Too many arguments, not enough ?")
        inserted = "'" + _sqlite_escape(str(obj)) + "'"
        query_str = query_str[:i] + inserted + query_str[i+1:]
        last = i + len(inserted) + 1

    result = _run_query(query_str)
    # parse the results
    if result[:6] == "Error:":
        raise Exception("Invalid query: " + 
                        repr(query_str) + "," + result[6:])
    return [x.split("|") for x in result.splitlines()]
