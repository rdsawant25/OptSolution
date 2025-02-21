#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
import time
import sys
sys.setrecursionlimit(10**8)
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight', 'ratio'])

class Knapsack:
    def __init__(self):
        self.opt_value = 0
        self.opt_taken = []
        self.opt_dict = {}
        self.node_visit = 0

    def bnb(self,capacity,items):
        depth = 0
        value = 0
        rem_cap = capacity
        # items = sorted(items, key=lambda x: x.ratio, reverse=True) #estimate by higher ratio
        # max_value = self.estimate(value, rem_cap, items)
        items = sorted(items, key=lambda x: x.value, reverse=True) #estimate by higher value
        max_value = self.estimate(value, rem_cap, items)
        self.opt_value = 0
        taken = [0] * len(items)
        self.opt_taken = copy.deepcopy(taken)
        possible_items = items
        # print(depth,value,rem_cap,max_value,items,taken,est_value)
        self.dfs(depth, value, rem_cap, max_value, possible_items, items, taken)

        for i,item in enumerate(items):
            self.opt_dict[item.index] = self.opt_taken[i]

        for i in range(len(self.opt_dict)):
            self.opt_taken[i] = self.opt_dict[i]

        # print(self.node_visit)

        return int(self.opt_value), self.opt_taken

    def dfs(self,depth,value,rem_cap,max_value,possible_items,items,taken):
        # print(depth,value,rem_cap,max_value,self.opt_value)
        self.node_visit += 1

        if len(possible_items) == 0:
            if max_value > self.opt_value:
                self.opt_value = value
                self.opt_taken = copy.deepcopy(taken)
                # print("Current Optimal as no possible items") if depth != len(items) \
                #     else print("Current Optimal")
            else:
                pass
                # print("Fathomed as no possible items") if depth != len(items) \
                #     else print("Fathomed")
            return

        if rem_cap < 0:
            # print("Infeasible")
            return

        if depth == len(items) and max_value >= self.opt_value:
            self.opt_value = value
            self.opt_taken = copy.deepcopy(taken)
            # print("Current Optimal")
            return

        if max_value < self.opt_value:
            # print("Fathomed")
            return

        depth += 1
        for i in [1,0]:
            taken[depth-1] = i
            rem_cap = self.bag_weight(rem_cap,taken[depth-1],items[depth-1])
            value = self.bag_value(taken[:depth],items[:depth]) if rem_cap >= 0 else value
            if rem_cap >= 0:
                max_value,possible_items = self.estimate_3(value, rem_cap, items[depth:])
            # max_value = self.estimate(value,rem_cap,items[depth:]) if rem_cap >= 0 else max_value
            self.dfs(depth,value,rem_cap,max_value,possible_items,items,taken)
            rem_cap = rem_cap + items[depth-1].weight
            # value = value - items[depth-1].value

    def bag_weight(self,rem_cap,taken,item):
        wgt = item.weight
        if taken==1:
            rem_cap = rem_cap - wgt
        else:
            rem_cap = rem_cap
        return rem_cap

    def bag_value(self,taken,items):
        value = 0
        for i in range(len(taken)):
            if taken[i]==1:
                item = items[i]
                val = item.value
                value = value + val
            else:
                continue
        return value

    def bag_value_2(self,value,taken,item):
        val = item.value
        if taken == 1:
            value += val
        else:
            value = value
        return value

    def estimate(self,value,rem_cap,items):
        max_value = value
        # items = sorted(items, key=lambda x: x.ratio, reverse=True)
        for i,item in enumerate(items):
            # print(i,item)
            val = item.value
            wgt = item.weight
            ratio = item.ratio
            if rem_cap - wgt >= 0:
                max_value += val
                rem_cap = rem_cap - wgt
            else:
                max_value += (rem_cap * ratio)
                rem_cap = 0
                break
        return max_value

    def estimate_2(self, value, rem_cap, items):
        max_value = value
        for i,item in enumerate(items):
            # print(i,item)
            val = item.value
            wgt = item.weight
            # ratio = item.ratio
            if rem_cap - wgt >= 0:
                max_value += val
                rem_cap = rem_cap - wgt
            else:
                continue

            if rem_cap <= 0:
                break
        return max_value

    def estimate_3(self,value,rem_cap,items):
        max_value = value
        possible_items = []
        max_cap = rem_cap
        # items = sorted(items, key=lambda x: x.ratio, reverse=True)
        for i,item in enumerate(items):
            # print(i,item)
            val = item.value
            wgt = item.weight
            ratio = item.ratio
            if wgt <= max_cap:
                possible_items.append(item)
                if rem_cap - wgt >= 0:
                    max_value += val
                    rem_cap = rem_cap - wgt
                else:
                    max_value += (rem_cap * ratio)
                    rem_cap = 0
                    break
            else:
                continue
        # print(max_value,possible_items)
        return max_value,possible_items

class DP:
    def __init__(self,items,capacity):
        self.items = items
        self.capacity = capacity
        self.table_row = [0 for i in range(capacity+1)]
        self.opt_table = []
        self.opt_dict = {}

    def get_curr_value(self,i,item,capacity):
        val = item.value
        wgt = item.weight
        value = val + self.opt_table[i][capacity-wgt]
        return value

    def get_prev_value(self,i,capacity):
        return self.opt_table[i][capacity]

    def fill_table(self,items,capacity):
        self.opt_table.append(copy.deepcopy(self.table_row))
        for i,item in enumerate(items):
            for c in range(item.weight,capacity+1):
                # if item.weight <= capacity:
                self.table_row[c] = max(self.get_prev_value(i,c),self.get_curr_value(i,item,c))

            self.opt_table.append(copy.deepcopy(self.table_row))

        # print("Completed")

    def get_results(self,items,capacity):
        opt_value = self.opt_table[len(self.opt_table)-1][capacity]
        for i,item in enumerate(reversed(items)):
            if self.opt_table[len(self.opt_table)-1-i][capacity] \
                    != self.opt_table[len(self.opt_table)-1-i-1][capacity]:
                self.opt_dict[item.index] = 1
                capacity = capacity - item.weight
            else:
                self.opt_dict[item.index] = 0

        opt_taken = []
        for i in range(len(self.opt_dict)):
            opt_taken.append(self.opt_dict[i])

        return opt_value, opt_taken

    def execute_dp(self,items,capacity):
        self.fill_table(items,capacity)
        value, taken = self.get_results(items,capacity)
        return value, taken

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), round(int(parts[0])/int(parts[1]),2)))

    # for item in items:
    #     if weight + item.weight <= capacity:
    #         taken[item.index] = 1
    #         value += item.value
    #         weight += item.weight
    start = time.time()
    if len(items) >= 10000:
        value = 0
        taken = [0] * len(items)
    else:
        # print(len(items),capacity)
        # value = 0
        # taken = [0] * len(items)
        if len(items) in [400, 10000]:
            value = 0
            taken = [0] * len(items)
            knapsack = Knapsack()
            value, taken = knapsack.bnb(capacity,items)
        else:
            dp = DP(items,capacity)
            value,taken = dp.execute_dp(items,capacity)
    end = time.time()
    # print(end-start)

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')





