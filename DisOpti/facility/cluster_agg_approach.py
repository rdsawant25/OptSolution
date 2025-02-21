from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from math import sin, cos, sqrt, atan2, radians

class get_cluster:
    def __init__(self,loc_df, facilities, customers):
        self.loc_df = loc_df
        self.facilities = facilities
        self.customers = customers

    def get_clusters_demand(self):
        x = self.loc_df.loc[:, ["x_loc", "y_loc"]].values
        # print(len(x))

        k = 5
        cluster = KMeans(n_clusters=k, init="k-means++", random_state=42)

        x_means = cluster.fit_predict(x)

        clusters = {}
        for i in self.loc_df.index:
            clusters[i] = x_means[i]

        # print(clusters)
        # print(x_means)

        df_cent = pd.DataFrame([[i, cluster.cluster_centers_[:, 0][i], cluster.cluster_centers_[:, 1][i]]
                                for i in range(k)],
                               columns=["cluster", "cen_x_loc", "cen_y_loc"])
        # df_cent.head()

        self.loc_df["cluster"] = None

        for i in clusters:
            self.loc_df.loc[i, ["cluster"]] = clusters[i]

        demand_df = self.loc_df[["index", "loctype", "y_loc", "x_loc", "demand", "capacity", "setup_cost", "cluster"]]
        demand_df = demand_df.merge(df_cent, on=["cluster"])
        demand_df["centroid_dist"] = demand_df.apply(
            lambda x: self.length(x["cen_x_loc"], x["cen_y_loc"], x["x_loc"], x["y_loc"]), axis=1)
        # demand_df.head()

        near_centroid_df = demand_df.loc[
            demand_df.loc[demand_df["loctype"] == "Facility", ["index", "cluster", "centroid_dist"]].groupby(
                "cluster").centroid_dist.idxmin(), ["index", "cluster"]]
        near_centroid_dict = near_centroid_df.set_index('cluster').to_dict()
        # near_centroid_dict

        agg_df = demand_df[["cluster", "demand", "cen_x_loc", "cen_y_loc"]].groupby(
            ["cluster", "cen_x_loc", "cen_y_loc"]).sum().reset_index()
        # agg_df["near_loc"] = agg_df["cluster"].apply(lambda x:near_centroid_dict["index"][x])
        # agg_df.head()

        print("demand: " + str(demand_df.demand.sum()))
        possible_fac = [near_centroid_dict["index"][i] for i in near_centroid_dict["index"]]
        print("possible_fac: " + str(len(possible_fac)))
        print("capacity: " + str(demand_df.loc[demand_df["index"].isin(possible_fac) == True, "capacity"].sum()))
        # print(agg_df.demand.sum())

        return demand_df, agg_df, possible_fac

    def get_results(self,demand_df, agg_df, result_df, possible_fac):
        demand_df.to_csv(r"results_data\demand_{0}_{1}.csv".format(str(len(self.facilities)),str(len(self.customers))),index=False)
        agg_df.to_csv(r"results_data\agg_{0}_{1}.csv".format(str(len(self.facilities)),str(len(self.customers))),index=False)
        result_df.to_csv(r"results_data\result_{0}_{1}.csv".format(str(len(self.facilities)),str(len(self.customers))),index=False)

        # agg_demand_dict = agg_df.set_index('cluster').to_dict()
        #
        # fac_loc = result_df.loc[result_df["data_type"] == "facility_loc", "source_index"].values
        #
        # fac_cust_ds = result_df.loc[
        #     result_df["data_type"] == "fac_cust_alloc", ["source_index", "destination_index"]].values
        #
        # fac_cust_loc_dict = {}
        # for i in range(len(fac_cust_ds)):
        #     # print(i)
        #     cust_ind = int(fac_cust_ds[i][1])
        #     fac_ind = int(fac_cust_ds[i][0])
        #     fac_cust_loc_dict[i] = [[demand_df.loc[(demand_df["loctype"] == "Facility") & (
        #                 demand_df["index"] == fac_ind), "x_loc"].values[0],
        #                              agg_demand_dict["cen_x_loc"][cust_ind]],
        #                             [demand_df.loc[(demand_df["loctype"] == "Facility") & (
        #                                         demand_df["index"] == fac_ind), "y_loc"].values[0],
        #                              agg_demand_dict["cen_y_loc"][cust_ind]]]
        #
        # fig = go.Figure(data=go.Scatter(x=demand_df.loc[demand_df["loctype"] == "Customer", "x_loc"],
        #                                 y=demand_df.loc[demand_df["loctype"] == "Customer", "y_loc"],
        #                                 mode='markers', marker_color=demand_df["demand"], opacity=0.3))
        #
        # fig.add_trace(go.Scatter(x=demand_df.loc[demand_df["index"].isin(possible_fac) == True, "x_loc"],
        #                          y=demand_df.loc[demand_df["index"].isin(possible_fac) == True, "y_loc"],
        #                          mode='markers', marker=dict(size=8, color="green"), name="possible_fac", opacity=0.3))
        #
        # fig.add_scatter(x=agg_df["cen_x_loc"], y=agg_df["cen_y_loc"], mode="markers",
        #                 marker=dict(color='black', size=8), name="Centroids")
        #
        # fig.add_trace(go.Scatter(x=agg_df.loc[agg_df["cluster"].isin(fac_loc) == True, "cen_x_loc"],
        #                          y=agg_df.loc[agg_df["cluster"].isin(fac_loc) == True, "cen_y_loc"],
        #                          mode="markers", marker=dict(size=8, color="blue"), name="Open Facilities"))
        #
        # for i in fac_cust_loc_dict:
        #     fig.add_scatter(x=fac_cust_loc_dict[i][0],
        #                     y=fac_cust_loc_dict[i][1],
        #                     mode='lines', marker=dict(color='royalblue'))

        # fig.write_image("50_6.png")
        # fig.show()

    def length(self, x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


