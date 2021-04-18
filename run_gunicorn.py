import os
import sys
from gunicorn.app.wsgiapp import run
port = os.environ['PORT']
sys.argv[-1:-1] = ['--bind', f':{port}']
print("sys.argv:", sys.argv)
run()
