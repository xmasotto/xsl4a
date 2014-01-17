import subprocess

from subprocess import Popen, PIPE, STDOUT

p = Popen(['sqlite3'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
command = 'hello'
print("Command: " + command)
print("Result: \n" + p.communicate(input=command+";")[0])
