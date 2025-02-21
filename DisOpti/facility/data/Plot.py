import pandas as pd
import plotly.express as px

class plot:
    def __init__(self,f_loc,c_loc):
        self.f_loc = f_loc
        self.c_loc = c_loc

    def scatter_plot(self):
        df = []
        for f_loc in self.f_loc:
            df.append(["Facility",f_loc.x,f_loc.y])

        for c_loc in self.c_loc:
            df.append(["Customer",c_loc.x,c_loc.y])
        print(df)
        df = pd.DataFrame(df,columns=["loctype","x_loc","y_loc"])
        print(df)
        fig = px.scatter(x=self.f_loc.x, y=self.f_loc.y, color="species",
                         size='petal_length', hover_data=['petal_width'])
        fig.show()
