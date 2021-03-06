import sys
import socket as sock
from random import randint

from simulate import VWSimulator

sys.path.append('../')
from simulator import *


'''Testing using all 5 3-day models on 2 hours of data from 2/14.'''
# Edit: running on 29 minutes or so due to time
socket_nums = []
for p in range(1, 6):
    model_name = 'models/%01d_pass' % p
    for m in range(5, 16):
        multiplier = m / 10
        socket_num = randint(10000, 65000)
        socket_nums.append(socket_num)
        os.system("pkill -9 -f 'vw.*--port {0}'".format(socket_num))
        os.system("~/vowpal_wabbit/vowpalwabbit/vw --daemon --port {0} --quiet -i {1}.model -t --num_children 1".format(socket_num, model_name))
        socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        socket.connect(('localhost', socket_num))
        queue_simulator(VWSimulator(socket, multiplier), 'VW (Model: {0}, Multiplier: {1})'.format(p, multiplier))
results = run_queue(start=(14, 0), stop=(14, 1), limit=15)
for socket_num in socket_nums:
    os.system("pkill -9 -f 'vw.*--port {0}'".format(socket_num))
