
import plotly.express as px

def standards_dot_plot_cv(df):

    fig = px.scatter(df, x="%CV", y="Metabolite name", title="iSTD %CV", labels={"%CV":"%CV"})
    fig.show()



