import torch
import plotly.express as px
import plotly.graph_objects as go
from plotly_resampler import FigureResampler
import numpy as np
from functools import cached_property
from plotly.io import to_html
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import mpld3

class Methods:
    
    def edge_list_with_wraparound(self, edges_lons):

        edges_wrap = np.zeros(len(edges_lons))
        for i in range(0, len(edges_lons), 3):
            lon_0, lon_1 = edges_lons[i], edges_lons[i+1]
            if np.abs(lon_1 - lon_0) > 180: 
                if lon_1 > lon_0:
                    lon_0 += 360
                else:
                    lon_1 += 360

            edges_wrap[i] = lon_0
            edges_wrap[i+1] = lon_1
            edges_wrap[i+2] = None
        
        return edges_wrap
    
    def plot_data_grid(self):
        """fig = FigureResampler(go.Figure(data=go.Scattergeo(
            lon=self.grid_lons,
            lat=self.grid_lats,
            mode='markers',
            marker=dict(
                size=3,
                color='blue',
                opacity=1
            )
        )))
        fig.update_layout(
            title_text='Data grid',
            geo_scope='europe', 
            width=1000, height=1000
        )"""
        fig = px.scatter(x=self.grid_lons, y=self.grid_lats,
                         range_x=self.xlim,
                         range_y=self.ylim,
                         width=1000,
                         height=1000,
                         title='Data grid'
        )
        fig.update_traces(marker=dict(color='blue', size=3))

        return fig

    def plot_hidden_grid(self):
        fig = px.scatter(x=self.mesh_lons, y=self.mesh_lats,
                         range_x=self.xlim,
                         range_y=self.ylim,
                         width=1000,
                         height=1000,
                         title='Hidden grid'
        )
        fig.update_traces(marker=dict(color='red', size=3))


        # This is better for visualization, with land showing and stuff, but waaaaaaay too slow.
        """        fig = FigureResampler(go.Figure(data=go.Scattergeo(
                    lon=self.mesh_lons,
                    lat=self.mesh_lats,
                    mode='markers',
                    marker=dict(
                        size=3,
                        color='red',
                        opacity=1
                    )
                )))
                fig.update_layout(
                    title_text='Hidden grid',
                    geo_scope='europe', 
                    width=1000, height=1000
                )"""

        return fig

    def dep_plot_encoder(self):
        
        #fig = go.Figure()
        
        print(self.dataframe)
        fig = px.scatter(self.dataframe, x='lons', y='lats', color='grid',
                         width=1000,
                         height=1000)
        #fig.add_trace(px.scatter(x=self.mesh_lons, y=self.mesh_lats))

        return fig

    def dep_plot_encoder(self):

        fig, ax = plt.subplots()
        ax.scatter(self.mesh_lons, self.mesh_lats)
        
        return mpld3.fig_to_html(fig)

    def plot_encoder(self):
        fig = px.line(x=self.edge_list_with_wraparound(self.encoder_edge_list[1]), y=self.encoder_edge_list[0],
                        width=1000,
                        height=1000)
        return fig
        



class Graph(Methods):
    def __init__(self, graph):
        self.graph = torch.load(graph, map_location=torch.device('cpu'), weights_only=False)
        print(self.graph)
        self.xlim = [-8, 40]
        self.ylim = [52, 78]

    @cached_property
    def grid_lats(self):
        return (self.graph['data']['x'][:,0]*180/np.pi).numpy()
    
    @cached_property
    def grid_lons(self):
        return (self.graph['data']['x'][:,1]*180/np.pi).numpy()

    @cached_property
    def mesh_lats(self):
        return (self.graph['hidden']['x'][:,0]*180/np.pi).numpy()
    
    @cached_property
    def mesh_lons(self):
        return (self.graph['hidden']['x'][:,1]*180/np.pi).numpy()

    @property
    def area_weights(self):
        return (self.graph['x']['area_weight']).numpy()
    
    @cached_property
    def dataframe(self):
        df = pd.DataFrame({
            'lons': self.grid_lons,
            'lats': self.grid_lats,
            'grid': ['grid']*len(self.grid_lats)
        })
        df = pd.concat([df,
            pd.DataFrame({
            'lons': self.mesh_lons,
            'lats': self.mesh_lats,
            'grid': ['hidden']*len(self.mesh_lats)
            })]
        )

        return df
    
    def edge_list(self, edges_key, src_mesh_key, dst_mesh_key):
        edge_x = []
        edge_y = []
        for n in range(self.graph[edges_key]["edge_index"].shape[1]):
            i, j = self.graph[edges_key]["edge_index"][:, n]
            ic = self.graph[src_mesh_key]['x'][i,:]
            jc = self.graph[dst_mesh_key]['x'][j,:]

            x0, y0 = np.rad2deg(ic)
            x1, y1 = np.rad2deg(jc)
            edge_x.append(x0.item())
            edge_x.append(x1.item())
            edge_x.append(None)

            if y0.item() > 180.:
                edge_y.append(y0.item() - 360)
            else:
                edge_y.append(y0.item())
            if y1.item() > 180.:
                edge_y.append(y1.item() - 360)
            else:
                edge_y.append(y1.item())
            edge_y.append(None)
        return np.array(edge_x), np.array(edge_y)

    @cached_property
    def encoder_edge_list(self):
        return self.edge_list(('data', 'to', 'hidden'), 'data', 'hidden')


if __name__ == '__main__':

    graph = Graph('/lustre/storeB/project/fou/hi/foccus/ppi-experiments/make-graph/run-anemoi-ocean/ppi/trim_edge_10_res_10_scale_10_thinning_2_cutoff_06_max_num_neighbours_100.pt')  
    #graph = Graph('/lustre/storeB/project/fou/hi/foccus/graphs/graph-2-12.pt')
    app = Flask(__name__)

    data_grid_html = to_html(graph.plot_data_grid(), full_html=False, include_plotlyjs='cdn')
    hidden_grid_html = to_html(graph.plot_hidden_grid(), full_html=False, include_plotlyjs='cdn')
    encoder_html = to_html(graph.plot_encoder(), full_html=False, include_plotlyjs='cdn') # ---> this one is insanely slow to zoom into

    @app.route("/")
    def home():
        return render_template('home.html')

    @app.route('/data_nodes')
    def data_nodes():
        return render_template('fig.html', plot_html=data_grid_html)
    
    @app.route('/hidden_nodes')
    def hidden_nodes():
        return render_template('fig.html', plot_html=hidden_grid_html)
    
    @app.route('/encoder')
    def encoder():
        return render_template('fig.html', plot_html=encoder_html)

    app.run(host='0.0.0.0', port=8080)

    