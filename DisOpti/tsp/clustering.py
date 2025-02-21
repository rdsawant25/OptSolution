from sklearn.cluster import KMeans

class clustering():
    def __init__(self,points):
        self.points = points
        self.k = 10

    def get_clusters(self):
        cluster = KMeans(n_clusters=self.k, init="k-means++", random_state=42)

        x = []
        for point in self.points:
            x.append([point.x,point.y])

        x_means = cluster.fit_predict(x)

        clusters = {}
        for i in range(len(self.points)):
            clusters[i] = x_means[i]

        return clusters