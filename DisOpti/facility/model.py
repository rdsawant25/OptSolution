from collections import namedtuple
import math
from pulp import *

class coin_model:
    def __init__(self,sets):
        self.f_set = sets.f_set
        self.c_set = sets.c_set
        self.f_c_set = sets.f_c_set
        self.FL = None

    def build_model(self):
        self.FL = LpProblem("Facility Location Problem", LpMinimize)

        #variables
        total_set_cost_var = LpVariable("SC",lowBound=0,cat="Continuous")
        total_dist_cost_var = LpVariable("DC",lowBound=0,cat="Continuous")
        facility_var = LpVariable.dicts("X",self.f_set,lowBound=0,upBound=1,cat="Integer")
        f_c_var = LpVariable.dicts("Y",(self.f_set,self.c_set),lowBound=0,upBound=1,cat="Integer")

        #objective
        self.FL += total_set_cost_var + total_dist_cost_var

        #constraints
        #total_set_cost
        self.FL += total_set_cost_var == lpSum(self.f_set[i]["setup_cost"]*facility_var[i] for i in self.f_set)
        self.FL += total_dist_cost_var == lpSum(self.f_c_set[(i,j)]["length"]
                                                * f_c_var[i][j] for (i,j) in self.f_c_set)

        #Customer must allocate
        for j in self.c_set:
            self.FL += lpSum(f_c_var[i][j] for i in self.f_set) == 1

        #Customer facility allocate
        for i in self.f_set:
            for j in self.c_set:
                self.FL += f_c_var[i][j] <= facility_var[i]

        #capacity const
        for i in self.f_set:
            self.FL += lpSum(self.c_set[j]["demand"]*f_c_var[i][j]
                             for j in self.c_set) <= self.f_set[i]["capacity"]*facility_var[i]

        #cuts
        # f_c_var[(0, 0)] + f_c_var[(0, 2)]+ f_c_var[(0, 3)] <= 1
        # f_c_var[(0, 1)] + f_c_var[(0, 2)]+ f_c_var[(0, 3)] <= 1
        # f_c_var[(1, 0)] + f_c_var[(1, 2)] + f_c_var[(1, 3)] <= 1
        # f_c_var[(1, 1)] + f_c_var[(1, 2)] + f_c_var[(1, 3)] <= 1
        # f_c_var[(1, 2)] + f_c_var[(1, 3)] <= 1
        # f_c_var[(0, 2)] + f_c_var[(0, 3)] <= 1

        # using cplex
        # solver = CPLEX_CMD(path="")
        # self.FL.solve(solver)

        #default COIN
        # solver = COIN_CMD(path="",timeLimit=60)
        self.FL.solve()

        # print(LpStatus[self.FL.status])
        # print(self.FL.objective.value())
        var_sol = {}
        for v in self.FL.variables():
            var_sol[v.name] = v.value()
            # print(v.name,v.value())

        f_c_sol = [0 for i in range(len(self.c_set))]
        for var in var_sol:
            if var.startswith("Y") and var_sol[var]==1:
                # print(var.split("_"))
                f_c_sol[int(var.split("_")[2])] = int(var.split("_")[1])
        # print(f_c_sol)
        return self.FL.objective.value(),f_c_sol

class Sets:
    def __init__(self, facilities, customers):
        self.facilities = facilities
        self.customers = customers

    def get_sets(self):
        self.f_set = self.get_facilities()
        self.c_set = self.get_customers()
        self.f_c_set = self.get_f_c_lengths()

    def get_facilities(self):
        f_set = {}
        for i, f in enumerate(self.facilities):
            f_set[f.index] = {
                "setup_cost" : f.setup_cost,
                "capacity" : f.capacity,
                "x" : f.location.x,
                "y" : f.location.y
            }

        return f_set

    def get_customers(self):
        c_set = {}
        for i, c in enumerate(self.customers):
            c_set[c.index] = {
                "demand": c.demand,
                "x": c.location.x,
                "y": c.location.y
            }

        return c_set

    def get_f_c_lengths(self):
        f_c_set = {}
        for i in self.f_set:
            for j in self.c_set:
                f_c_set[(i,j)] = {
                    "length": self.length(self.f_set[i]["x"],self.f_set[i]["y"],
                                          self.c_set[j]["x"],self.c_set[j]["y"])
                }

        return f_c_set

    @staticmethod
    def length(x1,y1,x2,y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


