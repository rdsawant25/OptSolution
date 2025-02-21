from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

class or_tools:
    def __init__(self,points):
        self.points = points
        self.distance_matrix, self.loc_for_data = self.compute_distance_matrix()
        self.routes = []

    def cal_dist(self, point1, point2):
        #reurning integer value as required in google OR tool
        return (math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2))

    def compute_distance_matrix(self):
        dist_mat = {}
        loc_for_data = []
        for from_node in range(len(self.points)):
            loc_for_data.append((self.points[from_node].x,self.points[from_node].y))
            dist_mat[from_node] = {}
            for to_node in range(len(self.points)):
                if from_node == to_node:
                    dist_mat[from_node][to_node] = 0
                else:
                    dist_mat[from_node][to_node] = int(self.cal_dist(self.points[from_node],self.points[to_node])*100)
        return dist_mat, loc_for_data

    def create_data_model(self):
        data = {}
        data["locations"] = self.loc_for_data
        data["num_vehicles"] = 1
        data["depot"] = 0
        return data

    def get_routes(self, solution, routing, manager):
        # Get vehicle routes and store them in a two dimensional array whose
        # i,j entry is the jth location visited by vehicle i along its route.
        routes = []
        routes_dist = []
        for route_nbr in range(routing.vehicles()):
            index = routing.Start(route_nbr)
            route = [manager.IndexToNode(index)]
            route_distance = 0
            while not routing.IsEnd(index):
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            routes.append(route)
            routes_dist.append(route_distance)
        return routes, routes_dist

    #Since ortools uses integer values in dist_matrix. Calculate original dist.
    def get_route_distace(self,route):
        start_node = route[0]
        end_node = route[-1]
        route_dist = self.cal_dist(self.points[start_node],self.points[end_node])
        for i in range(len(route)-1):
            route_dist += self.cal_dist(self.points[route[i]],self.points[route[i+1]])

        return route_dist

    def TSP_with_ortools(self):
        # Instantiate the data problem.
        data = self.create_data_model()

        # Create the routing index manager.
        # Index manager connects solver's indices with location numbers
        manager = pywrapcp.RoutingIndexManager(
            len(data["locations"]), data["num_vehicles"], data["depot"]
        )

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]

        # Create distance matrix callback and register with solver
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc. for TSP same as dist. It can be a function for other params as well
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic. Different sol strategy can be selected
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        # Setting search strategy. diff strategies are available
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING)
        search_parameters.time_limit.seconds = 900
        search_parameters.log_search = True

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        # print("Solver status: ", routing.status())
        # Get solution in list
        routes, routes_dist = self.get_routes(solution, routing, manager)
        # Display the routes
        # for i, route in enumerate(routes):
            # print('Route', i, route)
            # print('Route Distance', i, routes_dist[0])

        return routes[0][:-1], routes_dist[0]

