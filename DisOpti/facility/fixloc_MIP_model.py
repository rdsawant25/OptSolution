from pyomo.environ import *
import pandas as pd
import time
import os
from math import sin, cos, sqrt, atan2, radians

class get_fixloc_model:
    def __init__(self,fix_loc_result_df,facilities, customers):
        self.fix_loc_result_df = fix_loc_result_df
        self.facilities = facilities
        self.customers = customers

    def get_model(self):

        os.environ['NEOS_EMAIL'] = 'rdsawant25@gmail.com'
        neos= False
        s = time.time()
        M = ConcreteModel()
        sites = [i.index for i in self.customers]
        self.fix_loc = self.fix_loc_result_df.loc[self.fix_loc_result_df["data_type"]=="facility_loc","source_index"].values
        big_M = 100000

        distance_np = {}
        for i in sites:
            x1 = self.customers[i].location[0]
            y1 = self.customers[i].location[1]
            distance_np[i] = {}
            for j in self.fix_loc:
                x2 = self.facilities[j].location[0]
                y2 = self.facilities[j].location[1]
                distance_np[i][j] = self.length(x1, y1, x2, y2)


        def demand_function(M, i):
            return round(self.customers[i].demand, 2)

        M.I = self.fix_loc
        M.J = sites
        M.d = Param(M.J, initialize=demand_function)
        # M.distance = Param(M.I, M.J, initialize=distance_function)

        M.y = Var(M.I, M.J, within=Binary)
        M.x = Var(M.I, within=Binary)

        def distance_cost():
            return quicksum(
                round(distance_np[j][i], 2) * M.y[i, j] for i in M.I for j in M.J)

        def setup_cost():
            return quicksum(M.x[i] * self.facilities[i].setup_cost for i in M.I)

        print('data preprocessing done --------------------------------')

        exp = distance_cost() + setup_cost()

        def obj_expression(M):
            return exp

        M.OBJ = Objective(rule=obj_expression, sense=minimize)
        print('objective done', time.time() - s)

        def cust_alloc(M, j):
            return quicksum(M.y[i, j] for i in M.I) == 1
        M.c2 = Constraint(M.J, rule=cust_alloc)
        print('cust_alloc done', time.time() - s)

        def cap_const(M, i):
            return quicksum(M.y[i, j] * demand_function(M, j) for j in M.J) <= self.facilities[i].capacity * M.x[i]
        M.c3 = Constraint(M.I, rule=cap_const)
        print('c3 done', time.time() - s)

        def fac_cust_rel(M, i, j):
            return M.y[i, j] <= M.x[i]
        M.fac_cust_rel = Constraint(M.I, M.J, rule=fac_cust_rel)
        print('c4 done', time.time() - s)

        # M.pprint()
        print('Modeling done...', time.time() - s)
        # M.write("network_opt_fixloc" + str(len(sites)) + ".lp")
        if neos:
            solver_manager = SolverManagerFactory('neos')
            results = solver_manager.solve(M, opt='cplex')
        else:
            solvername = 'gurobi'
            opt = SolverFactory(solvername, tee=True)
            opt.options["Presolve"] = 1
            opt.options["MIPGap"] = 0.01
            opt.options["TimeLimit"] = 600
            # opt.options["Cuts"]=0.0
            # opt.options["Heuristics"]=0.8
            results = opt.solve(M, tee=True)
        print(results)
        result_data = []

        for i in M.I:
            if value(M.x[i]) == 1:
                result_data.append(
                    {"data_type": 'facility_loc', "source_index": i, "destination_index": None})

        for i in M.I:
            for j in M.J:
                if value(M.y[i, j]) == 1:
                    result_data.append({"data_type": 'fac_cust_alloc', "source_index": i, "destination_index": j})

        result_summary = pd.DataFrame(result_data)
        # result_summary.to_csv('result_'+str(len(sites))+'.csv',index=False)
        print(time.time() - s)

        f_c_sol_dict = {}
        for i in result_data:
            if i["data_type"] == "fac_cust_alloc":
                f_c_sol_dict[i["destination_index"]] = i["source_index"]

        f_c_sol = [0 for i in self.customers]
        for i in f_c_sol_dict:
            f_c_sol[i] = f_c_sol_dict[i]

        obj_value = value(M.OBJ)
        # # for v_data in M.component_data_objects(Var, descend_into=True):
        # #     print("Found: " + v_data.name + ", value = " + str(value(v_data)))
        #
        return obj_value, f_c_sol

    def length(self, x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

