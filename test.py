import subprocess

from subprocess import Popen, PIPE, STDOUT

command = "echo hello | sqlite3"
p = Popen(['sh'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
print("Command: " + command)
print("Result: \n" + p.communicate(input=command))
