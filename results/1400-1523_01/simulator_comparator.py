from collections import deque

from gametheory import AverageSingleID
from oneshot import MultiShot
from vwprediction.simulate import VWSimulator
from simulator import *

import socket as sock


class RunningAverageWithZeros(Simulator):
    """Represents a simple running average floor."""

    def __init__(self, *args, history_len=150, weight=10.0, **kwargs):
        super().__init__(*args, **kwargs)
        from collections import deque
        self.most_recent_bids = deque([0] * history_len, maxlen=history_len)
        self.weight = weight

    def calculate_price_floor(self, input_features):
        return self.weight * sum(self.most_recent_bids) / self.most_recent_bids.maxlen

    def process_line(self, line, input_features, bids):
        bid = 0.0 if len(bids) == 0 else bids[0]
        self.most_recent_bids.append(bid)


class RunningAverageWithoutZeros(Simulator):
    """Represents a simple running average floor."""

    def __init__(self, *args, history_len=25, weight=0.45, **kwargs):
        super().__init__(*args, **kwargs)
        from collections import deque
        self.most_recent_bids = deque([0] * history_len, maxlen=history_len)
        self.weight = weight

    def calculate_price_floor(self, input_features):
        return self.weight * sum(self.most_recent_bids) / self.most_recent_bids.maxlen

    def process_line(self, line, input_features, bids):
        if len(bids) > 0:
            self.most_recent_bids.append(bids[0])


class RunningAverageWithBuckets(Simulator):
    """Represents a simple running average floor."""

    def __init__(self, *args, history_len=25, weight=0.45, feature='site_id', **kwargs):
        super().__init__(*args, **kwargs)
        self.history_len = history_len
        self.feature = feature
        self.weight = weight
        self.history = {}

    def calculate_price_floor(self, input_features):
        if input_features[self.feature] not in self.history:
            self.history[input_features[self.feature]] = deque([0], maxlen=self.history_len)
        hist = self.history[input_features[self.feature]]
        return self.weight * sum(hist) / hist.maxlen

    def process_line(self, line, input_features, bids):
        bid = 0.0 if len(bids) == 0 else bids[0]
        self.history[input_features[self.feature]].append(bid)

# Run comparison


# --- Tune running average ---
# for h in [150, 160]:
#     for w in range(8, 20, 4):
#         queue_simulator(GlobalRunningAverage(history_len=h, weight=w), 'Avg: h=%d, w=%f' % (h, w))
# run_queue(start=(13, 12), stop=(13, 12), limit=5)

# default_simulator = DefaultSimulator(stop=(11, 23))
# naive_simulator_100 = NaiveSimulator(history_len=100)
# naive_simulator_200 = NaiveSimulator(history_len=200)
# oneshot_simulator = MultiShot(10)
# lp_simulator_5 = LinearProgramming(5, 0.000001, 1, 0.1 / 1000)
# lp_simulator_10 = LinearProgramming(10, 0.000001, 1, 0.1 / 1000)
#
# queue_simulator(naive_simulator_100, 'Naive-100')
# queue_simulator(naive_simulator_200, 'Naive-200')
# queue_simulator(oneshot_simulator, 'OneShot')
# queue_simulator(lp_simulator_5, 'LP-5')

# --- Test All ---
# Running average
queue_simulator(AverageSingleID(500, 0.6, 0.3, "site_id"), 'GT (High Revenue)')

oneshot_args = {'price_floor': 0.0002, 'eps': 1.0, 'lamb_h': 0.02, 'lamb_e': 0.9, 'lamb_l': 0.88, 'time': 0, 'M': 5}
queue_simulator(MultiShot(84, oneshot_args=oneshot_args), 'MultiShot with 84 Buckets')

socket_num = 12345
model_name = '~/polymorph-dpf/vwprediction/models/1_pass'
multiplier = 3.0
os.system("pkill -9 -f 'vw.*--port {0}'".format(socket_num))
os.system("~/vowpal_wabbit/vowpalwabbit/vw --daemon --port {0} --quiet -i {1}.model -t --num_children 1".format(socket_num, model_name))
socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket.connect(('localhost', socket_num))
queue_simulator(VWSimulator(socket, multiplier), 'VW (Multiplier: {0})'.format(multiplier))

queue_simulator(RunningAverageWithoutZeros(), 'Basic Running Average of Top Bids')
# queue_simulator(RunningAverageWithBuckets(), 'Running Average by site_id')
# queue_simulator(RunningAverageWithBuckets(feature='pub_network_id'), 'Running Average by pub_network_id')

results = run_queue(start=(14, 0))

os.system("pkill -9 -f 'vw.*--port {0}'".format(socket_num))
