#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import time
from collections import namedtuple
from TSP import *
from OR_Tools import *
from pyomo_model import *
from clustering import *
import random
import cProfile

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    solution = range(0, nodeCount)

    start_time = time.time()

    if len(points) >= 2000:
        # Using google OR tools
        if 0 > 1:
            print("Running ortools")
            tsp = or_tools(points)
            solution, obj = tsp.TSP_with_ortools()
            obj = tsp.get_route_distace(solution)
        # Using pyomo models
        elif 0 > 1:
            print("Running pyomo model")
            two_opt = TSP(points)
            two_opt.route = [node for node in solution]
            two_opt.run_neighbourhood()
            two_opt_obj = two_opt.cal_obj(two_opt.route)
            two_opt_solution = two_opt.route
            print("Sol from 2 opt: ", str(two_opt_obj))
            print(two_opt_solution)

            mip_model = pyomo_model(points)
            mip_model.initial_sol = two_opt_solution
            solution = mip_model.build_model()
            obj = mip_model.cal_obj(solution)

        # using cluster approach
        elif 0 > 1:
            cluster_start_time = time.time()
            cluster = clustering(points)
            clusters = cluster.get_clusters()
            cluster_end_time = time.time()
            print("Clustering Time: ", str(cluster_end_time - cluster_start_time))

            for k in range(cluster.k):
                print("cluster: ", str(k))
                cluster_solution = []
                for p in range(len(points)):
                    if clusters[p] == k:
                        cluster_solution.append(p)

                two_opt = TSP(points)
                two_opt.route = [node for node in cluster_solution]
                two_opt.run_neighbourhood()
                two_opt_obj = two_opt.cal_obj(two_opt.route)
                two_opt_solution = two_opt.route
                print("Sol from 2 opt: ", str(two_opt_obj))
                print(two_opt_solution)

                cluster_points = [points[node] for node in two_opt_solution]
                mip_model = pyomo_model(cluster_points)
                mip_model.initial_sol = two_opt_solution
                solution = mip_model.build_model()
                obj = mip_model.cal_obj(solution)
                print("Sol from pyomo: ", str(obj))
                print(solution)


    elif len(points) <= 2000:
        # Using 2 or 3 opt. 2 opt giving better results for these cases
        if 0 < 1:
            print("Running simulated annealing")
            tsp_sa = TSP(points)
            tsp_sa.route = [node for node in solution]
            # tsp.run_neighbourhood()
            # obj = tsp.cal_obj(tsp.route)
            # print('greedy sol: ',str(obj))
            cur_obj_values, best_obj_values, temp_values = tsp_sa.simulated_annealing()
            # for i in range(20):
            #     print(temp_values[i*100:(i+1)*100])
            # tsp.get_SA_plot(cur_obj_values, best_obj_values, temp_values)
            obj = tsp_sa.cal_obj(tsp_sa.route)
            solution = tsp_sa.route
            print("Sol from SA: ", str(obj))
            # print(solution)
            sa_end_time = time.time()
            print("Time: ", str(sa_end_time - start_time))

            # print("Running pyomo model")
            # tsp_pyomo_mip = TSP(points)
            # tsp_pyomo_mip.route = [node for node in solution]
            # # tsp_pyomo_mip.run_neighbourhood()
            # mip_model = pyomo_model(points)
            # mip_model.initial_sol = solution
            # solution = mip_model.build_model()
            # obj = mip_model.cal_obj(solution)
            # py_end_time = time.time()
            # print("Time: ",str(py_end_time-sa_end_time))

    end_time = time.time()
    print("Time: ",str(end_time-start_time))

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    random.seed(10)
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

