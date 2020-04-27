import os
from datetime import datetime

filename = str(datetime.now().date()) + '.log'
base_path = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.sep.join((base_path, 'logs'))
logfile = os.path.sep.join((log_directory, filename))
print(logfile)
with open(r'..\logs\2019-04-10.log', 'r', encoding='utf-8') as f:
    for line in f:
        if line:
            line = line.replace('#n#', '\n')
            print(line)
        else:
            print(None)

