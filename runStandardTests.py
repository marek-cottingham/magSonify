
import os

stream = os.popen('py -m unittest discover -s Tests_Unit -p "*Test.py" ')
output = stream.read()
print (output)

