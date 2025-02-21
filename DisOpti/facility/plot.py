import pandas as pd
import plotly.express as px

class Plot:
    def __init__(self, f_loc, c_loc):
        self.f_loc = f_loc
        self.c_loc = c_loc

    def scatter_plot(self):
        df = []
        for i,f_loc in enumerate(self.f_loc):
            df.append(["Facility",i, f_loc.location.x, f_loc.location.y, 0, f_loc.capacity, f_loc.setup_cost])

        for j,c_loc in enumerate(self.c_loc):
            df.append(["Customer",j, c_loc.location.x, c_loc.location.y, c_loc.demand, 0, 0])

        df = pd.DataFrame(df, columns=["loctype", "index", "x_loc", "y_loc", "demand", "capacity", "setup_cost"])
        # print(df)

        fig = px.scatter(df, x="x_loc", y="y_loc", color="loctype")
        # fig.show()

        return df
