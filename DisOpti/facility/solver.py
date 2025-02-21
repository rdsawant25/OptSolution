#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from model import Sets,coin_model
from plot import Plot
import math
from pulp import *

from cluster_agg_approach import *
from cluster_MIP_model import *
from fixloc_MIP_model import *

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    # build a trivial solution
    # pack the facilities one by one until all the customers are served
    # solution = [-1]*len(customers)
    # capacity_remaining = [f.capacity for f in facilities]
    #
    # facility_index = 0
    # for customer in customers:
    #     if capacity_remaining[facility_index] >= customer.demand:
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand
    #     else:
    #         facility_index += 1
    #         assert capacity_remaining[facility_index] >= customer.demand
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand
    #
    # used = [0]*len(facilities)
    # for facility_index in solution:
    #     used[facility_index] = 1
    #
    # # calculate the cost of the solution
    # obj = sum([f.setup_cost*used[f.index] for f in facilities])
    # for customer in customers:
    #     obj += length(customer.location, facilities[solution[customer.index]].location)

    #Scatter plot
    plot = Plot(facilities,customers)
    loc_df = plot.scatter_plot()
    # fig = plot.scatter_plot()
    # print(fig)

    solution = [-1]*len(customers)
    obj = 100000

    # MIP model using COIN
    if 0<1:
        # MIP model
        sets = Sets(facilities,customers)
        sets.get_sets()

        model = coin_model(sets)
        obj, solution = model.build_model()

        # prepare the solution in the specified output format
        output_data = '%.2f' % obj + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, solution))

        return output_data
    # Clustering and MIP model using NEOS
    elif 0>1:
        agg_demand = get_cluster(loc_df,facilities,customers)
        demand_df, agg_df, poss_fac = agg_demand.get_clusters_demand()

        cluster_model = get_cluster_model(agg_df,facilities,customers,poss_fac)
        result_df = cluster_model.get_model()

        agg_demand.get_results(demand_df, agg_df, result_df, poss_fac)

        fix_loc_model = get_fixloc_model(result_df,facilities,customers)
        obj, solution = fix_loc_model.get_model()

        # prepare the solution in the specified output format
        output_data = '%.2f' % obj + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, solution))

        return output_data

    else:
        pass

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

