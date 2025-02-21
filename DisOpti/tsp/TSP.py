import random
import time

import numpy as np
import math

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import cProfile
import pstats

import gc

class TSP:
    def __init__(self,points):
        self.points = points
        self.route = [] #self.run_nearest_neighbour()
        self.distance_matrix = self.compute_distance_matrix()

    def cal_dist(self,point1,point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

    def cal_obj(self, route):
        obj = self.cal_dist(self.points[route[-1]], self.points[route[0]])
        for i in range(len(route)-1):
            obj += self.cal_dist(self.points[route[i]], self.points[route[i+1]])
        return obj

    def compute_distance_matrix(self):
        dist_mat = {}
        for from_node in range(len(self.points)):
            dist_mat[from_node] = {}
            for to_node in range(len(self.points)):
                if from_node == to_node:
                    dist_mat[from_node][to_node] = 0
                else:
                    dist_mat[from_node][to_node] = int(self.cal_dist(self.points[from_node],self.points[to_node]))
        return dist_mat

    def perform_two_opt(self,cur_obj_value,i1,i2):
        points = self.points
        dist_mat = self.distance_matrix

        first_route = self.route[:i1+1]
        mid_route = self.route[i1+1:i2+1]
        last_route = self.route[i2+1:]

        #Connect last node of first_route to last node of mid_route
        #Connect first node of last_route to first node of mid_route
        new_mid_route = mid_route[::-1]

        # new_route = []
        # new_route.extend(first_route)
        # new_route.extend(new_mid_route)
        # new_route.extend(last_route)

        new_route = first_route + new_mid_route + last_route

        #Cal new obj value
        # rem_dist_1 = self.cal_dist(self.points[first_route[-1]],self.points[mid_route[0]])
        # rem_dist_2 = self.cal_dist(self.points[mid_route[-1]],self.points[last_route[0]])
        # add_dist_1 = self.cal_dist(self.points[first_route[-1]],self.points[new_mid_route[0]])
        # add_dist_2 = self.cal_dist(self.points[new_mid_route[-1]], self.points[last_route[0]])

        rem_dist_1 = dist_mat[first_route[-1]][mid_route[0]]
        rem_dist_2 = dist_mat[mid_route[-1]][last_route[0]]
        add_dist_1 = dist_mat[first_route[-1]][new_mid_route[0]]
        add_dist_2 = dist_mat[new_mid_route[-1]][last_route[0]]

        new_obj_value = cur_obj_value - rem_dist_1 - rem_dist_2 + add_dist_1 + add_dist_2

        return new_route, new_obj_value

    def select_nodes_for_two_opt(self, indexes):
        # first_node = random.choice(route[:-3])
        # i1 = route.index(first_node)
        # second_node = random.choice(route[i1+2:-1])
        # i2 = route.index(second_node)

        i1 = random.choice(indexes[:-3])
        i2 = random.choice(indexes[i1+2:-1])

        return i1,i2

    def perform_three_opt(self,cur_obj_value,i1,i2,i3):

        first_route = self.route[:i1+1]
        second_route = self.route[i1+1:i2+1]
        third_route = self.route[i2+1:i3+1]
        last_route = self.route[i3+1:]

        # Connect last node of first_route to first node of third_route
        # Connect first node of second_route to last node of third_route
        # Connect last  node of second_route to first node of last_route
        # in short swap 2 and 3 routes
        new_2_route = second_route[::-1]
        new_3_route = third_route[::-1]

        new_route = []
        new_route.extend(first_route)
        new_route.extend(new_2_route)
        new_route.extend(new_3_route)
        new_route.extend(last_route)

        #Cal new obj value
        rem_dist_1 = self.cal_dist(self.points[first_route[-1]],self.points[second_route[0]])
        rem_dist_2 = self.cal_dist(self.points[second_route[-1]],self.points[third_route[0]])
        rem_dist_3 = self.cal_dist(self.points[third_route[-1]], self.points[last_route[0]])
        add_dist_1 = self.cal_dist(self.points[first_route[-1]],self.points[new_2_route[0]])
        add_dist_2 = self.cal_dist(self.points[new_2_route[-1]], self.points[new_3_route[0]])
        add_dist_3 = self.cal_dist(self.points[new_3_route[-1]], self.points[last_route[0]])
        new_obj_value = cur_obj_value - rem_dist_1 - rem_dist_2 - rem_dist_3 + add_dist_1 + add_dist_2 + add_dist_3

        return new_route, new_obj_value

    def select_nodes_for_three_opt(self):
        first_node = random.choice(self.route[:-5])
        i1 = self.route.index(first_node)
        second_node = random.choice(self.route[i1+2:-3])
        i2 = self.route.index(second_node)
        third_node = random.choice(self.route[i2+2:-1])
        i3 = self.route.index(third_node)

        return i1,i2,i3

    def run_neighbourhood(self):
        if len(self.points) <= 2000:
            N = 100000 #No of iterations #Faster make iterations in 2-3 Millions
        # elif 500 <= len(self.points) <= 2000:
        #     N = 500000
        else:
            N = 500000

        i = 1 #Counter for iterations

        init_obj_value = self.cal_obj(self.route)
        cur_obj_value = init_obj_value
        self.route.append(self.route[0])
        indexes = [i for i in range(len(self.route))]
        while i <= N:

            # 2-opt
            i1, i2 = self.select_nodes_for_two_opt(indexes)
            new_route, new_obj_value = self.perform_two_opt(cur_obj_value, i1, i2)

            # 3-opt
            # i1, i2, i3 = self.select_nodes_for_three_opt()
            # new_route, new_obj_value = self.perform_three_opt(cur_obj_value, i1, i2, i3)

            if new_obj_value < cur_obj_value:
                self.route = new_route
                cur_obj_value = new_obj_value
            else:
                pass
            # print("{0} cur:{1} new:{2} i1:{3} i2:{4}".format(i,cur_obj_value,new_obj_value,i1,i2))
            i += 1

        self.route = self.route[:-1]

    def run_nearest_neighbour(self):
        visited = np.ones(len(self.points),dtype=bool)

        initial_sol = [0]
        cur_node = 0
        visited[0] = 0
        for i in range(len(self.points)-1):
            # return index having minimum distance from current point
            dist_array = np.array([self.cal_dist(self.points[cur_node],self.points[j]) for j in range(len(self.points))])
            min_dist_ind = np.argmin(dist_array[visited])
            min_dist_loc = np.arange(len(visited))[visited][min_dist_ind]
            initial_sol.append(min_dist_loc)
            visited[min_dist_loc] = 0
            cur_node = min_dist_loc
        # print(initial_sol)
        # print(self.cal_obj(initial_sol))
        return initial_sol

    def simulated_annealing(self):
        # route = self.route

        i = 1  # Counter for iterations
        a = 0.99 #Cooling rate
        # T_min = 0.00001 #Stopping criteria
        lot_count = 1 # iter lot to reduce temp
        reheat_temp = 5000 #T_init
        reheat = 2000 # reheat after iter
        reheat_freq = 100 # reheat after every 100 iter if no imp in best_obj
        reheat_count = 1 # No of reheats
        slow = 0 # binary for slow temp reached

        best_sol_counter = 0 # Counter when new best sol is found
        prob_sol_counter = 0  # Counter when prob is calc

        if len(self.points) < 100:
            N = 10000000 # No of iterations
            max_reheat = 0  # max reheats
            N_temp = 100 # No of iterations per temp
            N_temp_slow = 10000  # No of iterations per temp for slow cooling
            N_temp_counter = 1 # counter for temp iter
            T_init = 10000 # initial temp
            T = T_init  # initial temp
            slow_cooling_temp = 1000  # slow cooling after temp
            T_min = 0.00001  # Minimum temp
        elif 100 <= len(self.points) <= 500:
            N = 10000000 # No of iterations
            max_reheat = 0  # max reheats
            N_temp = 200 # No of iterations per temp
            N_temp_slow = 25000  # No of iterations per temp for slow cooling
            N_temp_counter = 1 # counter for temp iter
            T_init = 10000 # initial temp
            T = T_init  # initial temp
            slow_cooling_temp = 1000  # slow cooling after temp
            T_min = 0.00001  # Minimum temp
        elif 500 <= len(self.points) <= 1000:
            N = 100000000 # No of iterations
            max_reheat = 0  # max reheats
            N_temp = 500 # No of iterations per temp
            N_temp_slow = 50000  # No of iterations per temp for slow cooling
            N_temp_counter = 1 # counter for temp iter
            T_init = 100000 # initial temp
            T = T_init  # initial temp
            slow_cooling_temp = 1000  # slow cooling after temp
            T_min = 0.00001  # Minimum temp
        elif 1000 <= len(self.points) <= 2000:
            N = 100000000 # No of iterations
            max_reheat = 0  # max reheats
            N_temp = 500 # No of iterations per temp
            N_temp_slow = 75000  # No of iterations per temp for slow cooling
            N_temp_counter = 1 # counter for temp iter
            T_init = 1000000 # initial temp
            T = T_init  # initial temp
            slow_cooling_temp = 1000  # slow cooling after temp
            T_min = 0.00001  # Minimum temp
        else:
            N = 200
            max_reheat = 1

        init_obj_value = self.cal_obj(self.route)
        cur_obj_value = init_obj_value
        best_obj_value = cur_obj_value

        self.route.append(self.route[0])
        best_route = self.route[:]

        cur_obj_values = []
        best_obj_values = []
        temp_values = []

        indexes = [i for i in range(len(self.route))]
        cities = len(self.route)

        start_s = time.time()
        lot_start = start_s
        while i <= N:
            # iter_start = time.time()

            # Can add multiple heuristic and select one as in VNS shake method

            # 2-opt
            # i1, i2 = self.select_nodes_for_two_opt(indexes)
            i1 = random.choice(indexes[:-3])
            i2 = random.choice(indexes[i1 + 2:-1])
            # i1,i2 = random.choices(indexes[:-3],k=2)
            # i1 = random.randint(0,cities-1-3)
            # i2 = random.randint(i1+2,cities-1-1)
            new_route, new_obj_value = self.perform_two_opt(cur_obj_value, i1, i2)

            # 3-opt
            # i1, i2, i3 = self.select_nodes_for_three_opt()
            # new_route, new_obj_value = self.perform_three_opt(cur_obj_value, i1, i2, i3)

            if new_obj_value <= cur_obj_value:
                best_sol_counter += 1
                self.route = new_route[:]
                cur_obj_value = new_obj_value
                if new_obj_value < best_obj_value:
                    best_obj_value = new_obj_value
                    best_route = new_route[:]
            else:
                prob_sol_counter += 1
                prob = math.exp((cur_obj_value-new_obj_value)/T)
                rand_no = random.random()
                # print(prob, rand_no)
                if prob > rand_no:
                    cur_obj_value = new_obj_value
                    self.route = new_route[:]

            # print("{0} cur:{1} new:{2} i1:{3} i2:{4}".format(i,cur_obj_value,new_obj_value,i1,i2))
            # cur_obj_values.append(cur_obj_value)
            # best_obj_values.append(best_obj_value)
            # temp_values.append(T)

            if T < slow_cooling_temp and slow != 1:
                N_temp_counter = int((N_temp * N_temp_counter)/N_temp_slow) + 1
                N_temp = N_temp_slow
                slow = 1

            if i == N_temp * N_temp_counter:
                T = T * a #log cooling
                N_temp_counter += 1
            # T = math.sqrt(T) #Quad cooling

            # if i == N_temp * N_temp_counter:
            #     if T > slow_cooling_temp:
            #         T = T * a # Fast cooling for quick exploration
            #     elif T <= slow_cooling_temp:
            #         T = 10/math.log(i+1) # Slow cooling for fine-tuning or exploitation
            #     N_temp_counter += 1

            # Reheating for exploring new search space based on iterations
            # if (i > reheat * reheat_count and reheat_count <= max_reheat):
            #     if reheat_count == 3: # Reheating to initial temp
            #         T = T_init
            #     else:
            #         T = reheat_temp # Reheating to predefined temp
            #     reheat_count += 1

            # Reheating for exploring new search space based on best values
            # if i > reheat_freq:
            #     if (best_obj_values[i-1] < best_obj_values[i-1-reheat_freq] and reheat_count <= max_reheat):
            #         if reheat_count == 3: # Reheating to initial temp
            #             T = T_init
            #         else:
            #             T = reheat_temp # Reheating to predefined temp
            #         reheat_count += 1

            # Reheating for exploring new search space based on temp
            if T < 1 and reheat_count <= max_reheat:
                print("Reheating")
                T = T_init # Reheating to predefined temp
                reheat_count += 1

            if i == 1000000*lot_count:
                lot_end = time.time()
                print("Completed",str(lot_count),"M iterations in",str(round(lot_end-lot_start,2)),"sec", "Temp", str(round(T,2)),
                      "best", str(best_sol_counter), "prob",str(prob_sol_counter))
                best_sol_counter = 0
                prob_sol_counter = 0
                lot_start = time.time()
                lot_count += 1

            if T < T_min:
                print("T minimum reached.Stopping.........")
                break

            i += 1

            # iter_end = time.time()
            # print("iter time ",str(i),str(iter_end-iter_start))
            # print(i)

        # end_s = time.time()
        # print("time for all iters: ", end_s-start_s)

        print("End temp ", str(T))
        self.route = best_route[:]
        self.route = self.route[:-1]

        return cur_obj_values, best_obj_values, temp_values

    def get_SA_plot(self, cur_obj_values, best_obj_values, temp_values):
        iter = [i for i in range(len(cur_obj_values))]

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Create and style traces
        fig.add_trace(go.Scatter(x=iter, y=cur_obj_values, name='Current', mode='lines',
                                 line=dict(color='firebrick')))
        fig.add_trace(go.Scatter(x=iter, y=best_obj_values, name='Best', mode='lines',
                                 line=dict(color='royalblue')))
        fig.add_trace(go.Scatter(x=iter, y=temp_values, name="Temp", mode='lines',
                                 line=dict(color='orange')), secondary_y=True)
        fig.show()

if __name__ == '__main__':
    profiler = cProfile.Profile()

    import sys
    from collections import namedtuple

    random.seed(1)
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()

        Point = namedtuple("Point", ['x', 'y'])

        # parse the input
        lines = input_data.split('\n')

        nodeCount = int(lines[0])

        points = []
        for i in range(1, nodeCount+1):
            line = lines[i]
            parts = line.split()
            points.append(Point(float(parts[0]), float(parts[1])))

        solution = range(0, nodeCount)

        tsp = TSP(points)
        tsp.route = [node for node in solution]
        # profiler.enable()
        cur_obj_values, best_obj_values, temp_values = tsp.simulated_annealing()
        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('ncalls')
        # stats.print_stats()
        # tsp.get_SA_plot(cur_obj_values, best_obj_values, temp_values)
        obj = tsp.cal_obj(tsp.route)
        solution = tsp.route

        # prepare the solution in the specified output format
        output_data = '%.2f' % obj + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, solution))

        print(output_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')
