using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

class Point
{
    public double X { get; set; }
    public double Y { get; set; }

    public Point(double x, double y)
    {
        X = x;
        Y = y;
    }
}

class TSP
{
    private List<Point> points;
    private List<int> route;
    private Dictionary<int, Dictionary<int, double>> distanceMatrix;

    public TSP(List<Point> points)
    {
        this.points = points;
        this.route = new List<int>();
        this.distanceMatrix = ComputeDistanceMatrix();
    }

    private double CalculateDistance(Point p1, Point p2)
    {
        return Math.Sqrt(Math.Pow(p1.X - p2.X, 2) + Math.Pow(p1.Y - p2.Y, 2));
    }

    private double CalculateObjective(List<int> route)
    {
        double obj = CalculateDistance(points[route.Last()], points[route.First()]);
        for (int i = 0; i < route.Count - 1; i++)
        {
            obj += CalculateDistance(points[route[i]], points[route[i + 1]]);
        }
        return obj;
    }

    private Dictionary<int, Dictionary<int, double>> ComputeDistanceMatrix()
    {
        var distMatrix = new Dictionary<int, Dictionary<int, double>>();
        for (int fromNode = 0; fromNode < points.Count; fromNode++)
        {
            distMatrix[fromNode] = new Dictionary<int, double>();
            for (int toNode = 0; toNode < points.Count; toNode++)
            {
                distMatrix[fromNode][toNode] = (fromNode == toNode) ? 0 : CalculateDistance(points[fromNode], points[toNode]);
            }
        }
        return distMatrix;
    }

    private (List<int>, double) PerformTwoOpt(double currentObjValue, int i1, int i2)
    {
        var newRoute = new List<int>(route);
        newRoute.Reverse(i1 + 1, i2 - i1);

        double removedDist1 = distanceMatrix[route[i1]][route[i1 + 1]];
        double removedDist2 = distanceMatrix[route[i2]][route[(i2 + 1) % route.Count]];
        double addedDist1 = distanceMatrix[route[i1]][route[i2]];
        double addedDist2 = distanceMatrix[route[i1 + 1]][route[(i2 + 1) % route.Count]];

        double newObjValue = currentObjValue - removedDist1 - removedDist2 + addedDist1 + addedDist2;

        return (newRoute, newObjValue);
    }

    private (int, int) SelectNodesForTwoOpt()
    {
        Random random = new Random();
        int i1 = random.Next(0, route.Count - 3);
        int i2 = random.Next(i1 + 2, route.Count - 1);
        return (i1, i2);
    }

    public void SimulatedAnnealing()
    {
        Random random = new Random();
        int N = 500; // Number of iterations
        double T = 1000; // Initial temperature
        double T_min = 1; // Minimum temperature
        double alpha = 0.99; // Cooling rate

        double currentObjValue = CalculateObjective(route);
        double bestObjValue = currentObjValue;
        List<int> bestRoute = new List<int>(route);

        int iteration = 0;
        while (iteration < N && T > T_min)
        {
            var (i1, i2) = SelectNodesForTwoOpt();
            var (newRoute, newObjValue) = PerformTwoOpt(currentObjValue, i1, i2);

            if (newObjValue < currentObjValue || Math.Exp((currentObjValue - newObjValue) / T) > random.NextDouble())
            {
                route = newRoute;
                currentObjValue = newObjValue;

                if (newObjValue < bestObjValue)
                {
                    bestObjValue = newObjValue;
                    bestRoute = new List<int>(route);
                }
            }

            T *= alpha;
            iteration++;
        }

        route = bestRoute;
    }

    public void RunNearestNeighbour()
    {
        int n = points.Count;
        bool[] visited = new bool[n];
        route.Add(0);
        visited[0] = true;
        int currentNode = 0;

        for (int i = 0; i < n - 1; i++)
        {
            double minDistance = double.MaxValue;
            int nextNode = -1;

            for (int j = 0; j < n; j++)
            {
                if (!visited[j])
                {
                    double dist = distanceMatrix[currentNode][j];
                    if (dist < minDistance)
                    {
                        minDistance = dist;
                        nextNode = j;
                    }
                }
            }

            route.Add(nextNode);
            visited[nextNode] = true;
            currentNode = nextNode;
        }
    }

    public double GetObjective() => CalculateObjective(route);

    public List<int> GetRoute() => route;
}

class Program
{
    static void Main(string[] args)
    {
        if (args.Length >= 0)
        {
            // string fileLocation = args[0].Trim();
            string fileLocation = "C:\\Users\\olw05\\Downloads\\DisOpti\\tsp\\data\\tsp_51_1";
            var lines = File.ReadAllLines(fileLocation);

            int nodeCount = int.Parse(lines[0]);
            var points = new List<Point>();

            for (int i = 1; i <= nodeCount; i++)
            {
                var parts = lines[i].Split();
                double x = double.Parse(parts[0]);
                double y = double.Parse(parts[1]);
                points.Add(new Point(x, y));
            }

            var tsp = new TSP(points);
            // tsp.RunNearestNeighbour();
            tsp.SimulatedAnnealing();

            double objective = tsp.GetObjective();
            var solution = tsp.GetRoute();

            Console.WriteLine($"{objective:0.00} 0");
            Console.WriteLine(string.Join(" ", solution));
        }
        else
        {
            Console.WriteLine("This test requires an input file. Please provide a file path.");
        }
    }
}
