import os
from subprocess import Popen, PIPE, STDOUT

def query(filename, query_str, *rest):
    querylist = query_str.lower().split()

    # replace ? with escaped version of arguments
    last = 0
    for obj in rest:
        i = query_str.find("?", last)
        if i == -1:
            raise Exception("Too many arguments, not enough ?")
        query_str = query_str[:i] + repr(obj) + query_str[i+1:]
        last = i+1

    # try running piping the query to sqlite3
    try:
        p = Popen(['sqlite3', filename, '-batch'], 
                  stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        result = p.communicate(input=query_str+";")[0]
    except Exception:
        raise Exception("sqlite3 must be installed on your system.")

    # parse the results
    if result[:6] == "Error:":
        raise Exception("Invalid query: " + 
                        repr(query_str) + "," + result[6:])
    return [x.split("|") for x in result.splitlines()]
