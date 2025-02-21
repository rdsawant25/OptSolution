from pyomo.environ import *
import os
import math

class pyomo_model():
    def __init__(self,points):
        self.points = points
        self.initial_sol = []

    def cal_dist(self,point1,point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

    def cal_obj(self, route):
        obj = self.cal_dist(self.points[route[-1]], self.points[route[0]])
        for i in range(len(route)-1):
            obj += self.cal_dist(self.points[route[i]], self.points[route[i+1]])
        return obj

    # def create_sets(self):
    #     self.model.I = RangeSet(len(self.points))
    #
    # def create_vars(self):
    #     self.model.x = Var(self.model.I, self.model.I, within=Binary) # 1 is route is selected else 0
    #     self.model.u = Var(self.model.I, within=Binary) # Aux var for subtour elimination
    #
    # def obj_expression(self):
    #     return quicksum(self.cal_dist(self.points[i-1],self.points[j-1]) * self.model.x[i,j] for i in self.model.I for j in self.model.I)

    def build_model(self):
        # Define pyomo model
        M = ConcreteModel()

        # Sets
        M.I = RangeSet(len(self.points))

        # initial sol
        initial_sol_next_node = {}
        init_dict = {}
        for i in range(len(self.initial_sol)-1):
            cur_node = i+1
            next_node = i+2
            initial_sol_next_node[i] = self.initial_sol[i+1]
            init_dict[cur_node,next_node] = 1

        # Variables
        M.x = Var(M.I, M.I, within=Binary, initialize=init_dict)  # 1 is route is selected else 0
        M.u = Var(M.I, within=NonNegativeIntegers)  # Aux var for subtour elimination

        # Objective
        def obj_expression(M):
            return quicksum(self.cal_dist(self.points[i - 1], self.points[j - 1]) * M.x[i, j] for i in M.I for j in M.I)
        M.OBJ = Objective(rule=obj_expression, sense=minimize)

        # Constraints
        def enter_one_const(M, j):
            return quicksum(M.x[i,j] for i in M.I) == 1
        M.enter_one = Constraint(M.I, rule=enter_one_const)

        def exit_one_const(M, i):
            return quicksum(M.x[i,j] for j in M.I) == 1
        M.exit_one = Constraint(M.I, rule=exit_one_const)

        def subtour_elim(M, i, j):
            return M.u[i] - M.u[j] + 1 <= (len(self.points) - 1) * (1 - M.x[i,j])
        M.subtour_elim = Constraint(M.I-{1},M.I-{1}, rule=subtour_elim)

        def start_for_subtour_elim(M):
            return M.u[1] == 1
        M.start_for_subtour_elim = Constraint(rule=start_for_subtour_elim)

        def upper_bounds_for_aux_var(M,i):
            return M.u[i] <= len(self.points)
        M.upper_bounds_for_aux_var = Constraint(M.I-{1}, rule=upper_bounds_for_aux_var)

        def lower_bounds_for_aux_var(M,i):
            return M.u[i] >= 2
        M.lower_bounds_for_aux_var = Constraint(M.I-{1}, rule=lower_bounds_for_aux_var)

        os.environ['NEOS_EMAIL'] = 'rdsawant25@gmail.com'
        neos = True

        if neos:
            solver_manager = SolverManagerFactory('neos')
            results = solver_manager.solve(M, opt='cplex', tee=True)
        else:
            solvername = 'gurobi'
            opt = SolverFactory(solvername, tee=True)
            opt.options["Presolve"] = 1
            opt.options["MIPGap"] = 0.1
            # opt.options["Cuts"]=0.0
            opt.options["Heuristics"] = 0.8
            results = opt.solve(M, tee=True)
        # print(results)

        next_node = {}
        for i in M.I:
            for j in M.I:
                if value(M.x[i,j]) == 1:
                    next_node[i-1] = j-1

        sol = [0]
        cur_node = 0
        start_node = 0
        while len(sol) <= len(self.points):
            if next_node[cur_node] == start_node:
                break
            sol.append(next_node[cur_node])
            cur_node = next_node[cur_node]

        # print(sol)
        return sol


