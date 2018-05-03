import simulator
import numpy as np


class CleverBruteForce(simulator.Simulator):
    def __init__(self, memory, discount, default, *args, **kwargs):
        """
        :param memory: (int) the number of previous bids to remember; the space
            complexity of this algorithm is roughly O(memory)
        :param discount: (double) a parameter which specifies the amount of
            underestimation over the optimal price floor calculated
        :param default: (double) the default price floor to output, given not
            enough information
        """
        super().__init__(*args, **kwargs)
        self.memory = memory
        self.default = default
        self.discount = discount

        self.position = 0
        self.complete = False
        self.uppers = np.zeros(memory)
        self.lowers = np.zeros(memory)

    def calculate_price_floor(self, input_features):
        """
        :param input_features: {str: obj} provided feature information
        :return: (float) the price floor to set
        """
        if not self.complete:
            return self.default

        best = max(self.uppers, key=lambda price: self.compute_revenue(price))
        return best

    def process_line(self, line, input_features, bids):
        """
        :param line: {str: obj} provided line information
        :param input_features: {str: obj} provided feature information
        :param bids: [float] bids given during auction
        :return:
        """
        if not bids:
            return

        amounts = sorted(bids, reverse=True)
        first = amounts[0]
        second = amounts[1] if len(amounts) > 1 else 0
        self.uppers[self.position] = first
        self.lowers[self.position] = second

        self.position += 1
        if self.position == self.memory:
            self.complete = True
            self.position = 0

    def compute_revenue(self, price):
        """
        :param price: (float) the potential reserve price to consider
        :return: (float) the revenue generated by this price floor based on the

        """
        total = 0
        for pos in range(self.memory):
            if price > self.uppers[pos]:
                total += 0
            elif price < self.lowers[pos]:
                total += self.lowers[pos]
            else:
                total += price
        return total


if __name__ == '__main__':
    settings = {
        'memory': 100,
        'discount': 1,
        'default': 0.1 / 1000
    }
    test = CleverBruteForce(limit=1, download=False, delete=False, **settings)
    test.run_simulation()
