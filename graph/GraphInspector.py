import numpy as np
import matplotlib.pyplot as plt
import torch
from torch_geometric.data import HeteroData
from functools import cached_property
import cartopy.crs as ccrs
from typing import Optional


class GraphInspector:
    def __init__(self, graph_data, grid_key = 'grid', hidden_key = 'hidden', coords_key='coords', obs_key=None, verbose = True) -> None:
        if type(graph_data) == HeteroData:
            self.graph_data = graph_data
        elif type(graph_data) == str:
            try:
                self.graph_data = torch.load(graph_data, map_location=torch.device('cpu'), weights_only=False)
            except:
                raise RuntimeError("Could not open graph data file")
        else:
            raise RuntimeError("Invalid graph_data input")
        
        self.grid_key = grid_key
        self.hidden_key = hidden_key
        self.obs_key = obs_key
        self.e2h_key = (grid_key, 'to', hidden_key)
        self.h2e_key = (hidden_key, 'to', grid_key)
        self.h2h_key = (hidden_key, 'to', hidden_key)
        self.o2h_key = (obs_key, 'to', hidden_key)
        self.h2o_key = (hidden_key, 'to', obs_key)
        self.coords_key = coords_key

        try:
            self.graph_data[self.grid_key]
        except KeyError:
            raise KeyError(f"Grid key '{grid_key}' not found, try to initialize with kwarg grid_key='{list(self.graph_data.keys())[0]}'")
        try:
            self.graph_data[self.h2h_key]
        except KeyError:
            raise KeyError(f"Hidden key '{hidden_key}' not found, try to initialize with kwarg hidden_key='{list(self.graph_data.keys())[1]}'")                  
        if obs_key is not None:
            try: 
                self.graph_data[self.obs_key]
            except KeyError:
                raise KeyError(f"Obs key '{obs_key}' not found in graph object")
            

    @property
    def n_grid_nodes(self):
        return self.graph_data[self.grid_key][self.coords_key].shape[0]
    
    @property
    def n_mesh_nodes(self):
        return self.graph_data[self.hidden_key][self.coords_key].shape[0]
    
    @property
    def n_obs_nodes(self):
        return self.graph_data[self.obs_key]['coords'].shape[0]

    @cached_property
    def grid_lats(self):
        return (self.graph_data[self.grid_key][self.coords_key][:,0]*180/np.pi).numpy()
    
    @cached_property
    def grid_lons(self):
        grid_lons = (self.graph_data[self.grid_key][self.coords_key][:,1]*180/np.pi).numpy()    
        #Shift these to -180, 180 for consistency when plotting
        #grid_lons[grid_lons > 180.] = grid_lons[grid_lons > 180.] - 360.
        return grid_lons
    
    @cached_property
    def mesh_lats(self):
        return (self.graph_data[self.hidden_key][self.coords_key][:,0]*180/np.pi).numpy()
    
    @cached_property
    def mesh_lons(self):
        return (self.graph_data[self.hidden_key][self.coords_key][:,1]*180/np.pi).numpy()
    
    @cached_property
    def obs_lats(self):
        return (self.graph_data[self.obs_key]['coords'][:,0]*180/np.pi).numpy()
    
    @cached_property
    def obs_lons(self):
        obs_lons = (self.graph_data[self.obs_key]['coords'][:,1]*180/np.pi).numpy()
        obs_lons[obs_lons > 180.] = obs_lons[obs_lons > 180.] - 360
        return obs_lons

    '''
    @cached_property
    def grid_edge_weights(self):
        return (self.graph_data[self.grid_key]['edge_attr'][:,0]).numpy()
    '''
    @property
    def area_weights(self):
        return (self.graph_data[self.grid_key][self.coords_key]).numpy()
    
    @property
    def obs_area_weights(self):
        return (self.graph_data[self.obs_key]['weights']).numpy()
    
    @property
    def mesh_edge_weights(self):
        return (self.graph_data[self.h2h_key][self.coords_key][:,0]).numpy()
    
    @property
    def encoder_edge_weights(self):
        return (self.graph_data[self.e2h_key][self.coords_key][:,0]).numpy()
    
    @property
    def obs_encoder_edge_weights(self):
        return (self.graph_data[self.o2h_key]['edge_attr'][:,0]).numpy()

    @property
    def decoder_edge_weights(self):
        return (self.graph_data[self.h2e_key][self.coords_key][:,0]).numpy()
    
    @property
    def obs_decoder_edge_weights(self):
        return (self.graph_data[self.h2o_key]['edge_attr'][:,0]).numpy()

    @property
    def encoder_grid_orphans(self):
        encoder_grid_nodes = set(self.graph_data[self.e2h_key]['edge_index'][0].numpy())
        all_grid_nodes = set(np.array(range(self.n_grid_nodes)))
        return list(all_grid_nodes - encoder_grid_nodes)
    
    @property 
    def obs_encoder_grid_orphans(self):
        obs_encoder_grid_nodes = set(self.graph_data[self.o2h_key]['edge_index'][0].numpy())
        all_obs_grid_nodes = set(np.array(range(self.n_obs_nodes)))
        return list(all_obs_grid_nodes - obs_encoder_grid_nodes)

    @property
    def encoder_grid_orphans_coords(self):
        coords = np.zeros((2, len(self.encoder_grid_orphans)))
        for ind, i in enumerate(self.encoder_grid_orphans):
            coords[0,ind] = self.grid_lats[i]
            coords[1,ind] = self.grid_lons[i]

        return coords
    
    @property
    def obs_encoder_grid_orphans_coords(self):
        coords = np.zeros((2, len(self.obs_encoder_grid_orphans)))
        for ind, i in enumerate(self.obs_encoder_grid_orphans):
            coords[0,ind] = self.obs_lats[i]
            coords[1,ind] = self.obs_lons[i]

        return coords
    
    @property 
    def encoder_mesh_orphans(self):
        encoder_mesh_nodes = set(self.graph_data[self.e2h_key]['edge_index'][1].numpy())
        all_mesh_nodes = set(np.array(range(self.n_mesh_nodes)))
        return list(all_mesh_nodes - encoder_mesh_nodes)

    @property 
    def obs_encoder_mesh_orphans(self):
        obs_encoder_mesh_nodes = set(self.graph_data[self.o2h_key]['edge_index'][1].numpy())
        all_mesh_nodes = set(np.array(range(self.n_mesh_nodes)))
        return list(all_mesh_nodes - obs_encoder_mesh_nodes)
    
    @property
    def encoder_mesh_orphans_coords(self):
        coords = np.zeros((2, len(self.encoder_mesh_orphans)))
        for ind, i in enumerate(self.encoder_mesh_orphans):
            coords[0,ind] = self.mesh_lats[i]
            coords[1,ind] = self.mesh_lons[i]

        return coords
    
    @property
    def obs_encoder_mesh_orphans_coords(self):
        coords = np.zeros((2, len(self.obs_encoder_mesh_orphans)))
        for ind, i in enumerate(self.obs_encoder_mesh_orphans):
            coords[0,ind] = self.mesh_lats[i]
            coords[1,ind] = self.mesh_lons[i]

        return coords

    @property
    def decoder_grid_orphans(self):
        decoder_grid_nodes = set(self.graph_data[self.h2e_key]['edge_index'][1].numpy())
        all_grid_nodes = set(np.array(range(self.n_grid_nodes)))
        return list(all_grid_nodes  - decoder_grid_nodes)
    
    @property
    def obs_decoder_grid_orphans(self):
        obs_decoder_grid_nodes = set(self.graph_data[self.h2o_key]['edge_index'][1].numpy())
        all_obs_nodes = set(np.array(range(self.n_obs_nodes)))
        return list(all_obs_nodes  - obs_decoder_grid_nodes)
    
    @property
    def decoder_grid_orphans_coords(self):
        coords = np.zeros((2, len(self.decoder_grid_orphans)))
        for ind, i in enumerate(self.decoder_grid_orphans):
            coords[0,ind] = self.grid_lats[i]
            coords[1,ind] = self.grid_lons[i]

        return coords
    
    @property
    def obs_decoder_grid_orphans_coords(self):
        coords = np.zeros((2, len(self.obs_decoder_grid_orphans)))
        for ind, i in enumerate(self.obs_decoder_grid_orphans):
            coords[0,ind] = self.obs_lats[i]
            coords[1,ind] = self.obs_lons[i]

        return coords

    @property
    def decoder_mesh_orphans(self):
        decoder_mesh_nodes = set(self.graph_data[self.h2e_key]['edge_index'][0].numpy())
        all_mesh_nodes = set(np.array(range(self.n_mesh_nodes)))
        return list(all_mesh_nodes - decoder_mesh_nodes)
    
    @property
    def obs_decoder_mesh_orphans(self):
        obs_decoder_mesh_nodes = set(self.graph_data[self.h2o_key]['edge_index'][0].numpy())
        all_mesh_nodes = set(np.array(range(self.n_mesh_nodes)))
        return list(all_mesh_nodes - obs_decoder_mesh_nodes)
    
    @property
    def decoder_mesh_orphans_coords(self):
        coords = np.zeros((2, len(self.decoder_mesh_orphans)))
        for ind, i in enumerate(self.decoder_mesh_orphans):
            coords[0,ind] = self.mesh_lats[i]
            coords[1,ind] = self.mesh_lons[i]

        return coords
    
    @property
    def obs_decoder_mesh_orphans_coords(self):
        coords = np.zeros((2, len(self.obs_decoder_mesh_orphans)))
        for ind, i in enumerate(self.obs_decoder_mesh_orphans):
            coords[0,ind] = self.mesh_lats[i]
            coords[1,ind] = self.mesh_lons[i]

        return coords
    
    def has_orphans(self, verbose = True):
        orphans = False
        if self.encoder_grid_orphans != []:
            if verbose:
                print("Encoder has {} grid orhpans".format(len(self.encoder_grid_orphans)))
            orphans = True
        if self.encoder_mesh_orphans != []:
            if verbose:
                print("Encoder has {} mesh orphans".format(len(self.encoder_mesh_orphans)))
            orphans = True
        if self.decoder_grid_orphans != []:
            if verbose:
                print("Decoder has {} grid orhpans".format(len(self.decoder_grid_orphans)))
            orphans = True
        if self.decoder_mesh_orphans != []:
            if verbose:
                print("Decoder has {} mesh orphans".format(len(self.decoder_mesh_orphans)))
            orphans = True
        if orphans == False:
            if verbose:
                print("Encoder and decoder have no orphans")
        return orphans
    
    def has_obs_orphans(self, verbose = True):
        orphans = False
        if self.obs_encoder_grid_orphans != []:
            if verbose:
                print("Obs encoder has {} grid orhpans".format(len(self.obs_encoder_grid_orphans)))
            orphans = True
        if self.obs_encoder_mesh_orphans != []:
            if verbose:
                print("Obs encoder has {} mesh orphans".format(len(self.obs_encoder_mesh_orphans)))
            orphans = True
        if self.obs_decoder_grid_orphans != []:
            if verbose:
                print("Obs decoder has {} grid orhpans".format(len(self.obs_decoder_grid_orphans)))
            orphans = True
        if self.obs_decoder_mesh_orphans != []:
            if verbose:
                print("Obs decoder has {} mesh orphans".format(len(self.obs_decoder_mesh_orphans)))
            orphans = True
        if orphans == False:
            if verbose:
                print("Obs encoder and decoder have no orphans")
        return orphans
    
#    def edge_list(self, grph_in, plt_ids):
    def edge_list(self, edges_key, src_mesh_key, dst_mesh_key):
        edge_x = []
        edge_y = []
#        for n in range(grph_in["edge_index"].shape[1]):
        for n in range(self.graph_data[edges_key]["edge_index"].shape[1]):
#            i, j = grph_in["edge_index"][:, n]
#            ic = grph_in[plt_ids[0]][i, :]
#            jc = grph_in[plt_ids[1]][j, :]
            i, j = self.graph_data[edges_key]["edge_index"][:, n]
            ic = self.graph_data[src_mesh_key][self.coords_key][i,:]
            jc = self.graph_data[dst_mesh_key][self.coords_key][j,:]

            x0, y0 = np.rad2deg(ic)
            x1, y1 = np.rad2deg(jc)
            edge_x.append(x0.item())
            edge_x.append(x1.item())
            edge_x.append(None)
            # Apply same shift here that we did to grid lons, turns out this works better when plotting
            if y0.item() > 180.:
                edge_y.append(y0.item() - 360)
            else:
                edge_y.append(y0.item())
            if y1.item() > 180.:
                edge_y.append(y1.item() - 360)
            else:
                edge_y.append(y1.item())
#            edge_y.append(y0,item())
#            edge_y.append(y1.item())
            edge_y.append(None)
        return np.array(edge_x), np.array(edge_y)

#    @cached_property
#    def grid_edge_list(self):
#        return self.edge_list(self.graph_data[self.e2e_key], ('coords', 'coords'))

    @cached_property
    def mesh_edge_list(self):
        return self.edge_list(self.h2h_key, self.hidden_key, self.hidden_key)

    @cached_property
    def encoder_edge_list(self):
#        return self.edge_list(self.graph_data[self.e2h_key], ('coords', 'coords'))
        return self.edge_list(self.e2h_key, self.grid_key, self.hidden_key)
    
    @cached_property
    def obs_encoder_edge_list(self):
        return self.edge_list(self.o2h_key, self.obs_key, self.hidden_key)

    @cached_property
    def decoder_edge_list(self):
        return self.edge_list(self.h2e_key, self.hidden_key, self.grid_key)
    
    @cached_property
    def obs_decoder_edge_list(self):
        return self.edge_list(self.h2o_key, self.hidden_key, self.obs_key)
    
    def edge_list_with_wraparound(self, edges_lons):
        # Assumes edges is on the format (lon0, lon1, None, lon2, lon3, None) with edge lon0->lon1, lon2->lon3 etc
        edges_wrap = np.zeros(len(edges_lons))
        for i in range(0, len(edges_lons), 3):
            lon_0, lon_1 = edges_lons[i], edges_lons[i+1]
            if np.abs(lon_1 - lon_0) > 180: #Need to change this, want to do it for edges that cross 180 deg east
                if lon_1 > lon_0:
                    lon_0 += 360
                else:
                    lon_1 += 360
        #    if lon_0 > 90 and lon_1 < -90:
        #        lon_1 += 360
        #    if lon_1 > 90 and lon_0 < -90:
        #        lon_0 += 360
            edges_wrap[i] = lon_0
            edges_wrap[i+1] = lon_1
            edges_wrap[i+2] = None
        
        return edges_wrap

    def plot_encoder(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw = dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.plot(self.edge_list_with_wraparound(self.encoder_edge_list[1]), self.encoder_edge_list[0], lw=0.2, label='encoder', color='black')
        ax.scatter(self.grid_lons, self.grid_lats, marker='.', s=10, color='blue', label = 'grid')
        ax.scatter(self.mesh_lons, self.mesh_lats, marker='.', s=100, color='red', label = 'mesh')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Encoder')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax

    def plot_obs_encoder(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw = dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.plot(self.edge_list_with_wraparound(self.obs_encoder_edge_list[1]), self.obs_encoder_edge_list[0], lw=0.2, label='obs encoder', color='black')
        ax.scatter(self.obs_lons, self.obs_lats, marker='.', s=10, color='blue', label = 'obs grid')
        ax.scatter(self.mesh_lons, self.mesh_lats, marker='.', s=100, color='red', label = 'mesh')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Obs encoder')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax  
    
    def plot_decoder(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.plot(self.edge_list_with_wraparound(self.decoder_edge_list[1]), self.decoder_edge_list[0], lw=0.2, label='decoder', color='black')
        ax.scatter(self.grid_lons, self.grid_lats, marker='.', s=10, color='blue', label = 'grid')
        ax.scatter(self.mesh_lons, self.mesh_lats, marker='.', s=100, color='darkorange', label = 'mesh')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Decoder')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax   

    def plot_obs_decoder(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.plot(self.edge_list_with_wraparound(self.obs_decoder_edge_list[1]), self.obs_decoder_edge_list[0], lw=0.2, label='obs decoder', color='black')
        ax.scatter(self.obs_lons, self.obs_lats, marker='.', s=10, color='blue', label = 'obs grid')
        ax.scatter(self.mesh_lons, self.mesh_lats, marker='.', s=100, color='darkorange', label = 'mesh')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Obs decoder')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax   
    
    def plot_grid(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.scatter(self.grid_lons, self.grid_lats, marker='.', s=10, color='blue', label='grid')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Grid')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax 
    
    def plot_obs_grid(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.scatter(self.obs_lons, self.obs_lats, marker='.', s=10, color='blue', label='obs grid')
        ax.gridlines(ls = '--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Obs grid')
        fig.legend()
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax 
            
    def plot_mesh(self, xlim=(-180, 180), ylim=(-90, 90), save_path=None):
        import matplotlib.cm as cm
        import matplotlib.colors as mcolors
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        
        mesh_edge_lons = self.edge_list_with_wraparound(self.mesh_edge_list[1])
        mesh_edge_lats = self.mesh_edge_list[0]
        n_lines = self.graph_data[self.h2h_key]['edge_index'].shape[1]
        edge_weights = self.mesh_edge_weights

        cmap = cm.get_cmap('gist_rainbow', n_lines)
        norm = mcolors.Normalize(vmin=min(edge_weights), vmax=max(edge_weights))

        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.scatter(self.mesh_lons, self.mesh_lats, marker='.', s=10, color='gray')
        for i in range(n_lines):
            color = cmap(norm(edge_weights[i]))
            ax.plot(mesh_edge_lons[3*i:3*i+2], mesh_edge_lats[3*i:3*i+2], lw=edge_weights[i], color=color)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
        fig.colorbar(sm, cax=cax, label='edge weight')
        fig.suptitle('Mesh (note that connections over the 180 -> -180 boundary are not plotted)')
        gl = ax.gridlines(ls='--', draw_labels=True, alpha=0.1)
        gl.top_labels= False
        gl.right_labels = False
        if save_path is not None:
            fig.savefig(save_path)        
        return fig, ax
    
    def plot_orphans(self, xlim=(-180, 180), ylim=(-90,90), save_path=None):
        encoder_grid_orphans = self.encoder_grid_orphans_coords
        encoder_mesh_orphans = self.encoder_mesh_orphans_coords
        decoder_grid_orphans = self.decoder_grid_orphans_coords
        decoder_mesh_orphans = self.decoder_mesh_orphans_coords

        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.scatter(encoder_grid_orphans[1], encoder_grid_orphans[0], marker='.', color='blue', label='encoder grid orphans')
        ax.scatter(decoder_mesh_orphans[1], decoder_mesh_orphans[0], marker='.', color='darkorange', label='decoder mesh orphans')
        ax.scatter(encoder_mesh_orphans[1], encoder_mesh_orphans[0], marker='.', color='red', label='encoder mesh orphans')
        ax.scatter(decoder_grid_orphans[1], decoder_grid_orphans[0], marker='.', color='green', label='decoder grid orphans')
        ax.legend()
        ax.gridlines(ls='--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Orphans in encoder and decoder')
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax
    
    def plot_obs_orphans(self, xlim=(-180, 180), ylim=(-90,90), save_path=None):
        encoder_grid_orphans = self.obs_encoder_grid_orphans_coords
        encoder_mesh_orphans = self.obs_encoder_mesh_orphans_coords
        decoder_grid_orphans = self.obs_decoder_grid_orphans_coords
        decoder_mesh_orphans = self.obs_decoder_mesh_orphans_coords

        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.scatter(encoder_grid_orphans[1], encoder_grid_orphans[0], marker='.', color='blue', label='obs encoder grid orphans')
        ax.scatter(decoder_mesh_orphans[1], decoder_mesh_orphans[0], marker='.', color='darkorange', label='obs decoder mesh orphans')
        ax.scatter(encoder_mesh_orphans[1], encoder_mesh_orphans[0], marker='.', color='red', label='obs encoder mesh orphans')
        ax.scatter(decoder_grid_orphans[1], decoder_grid_orphans[0], marker='.', color='green', label='obs decoder grid orphans')
        ax.legend()
        ax.gridlines(ls='--', draw_labels=True, alpha=0.1)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.suptitle('Orphans in obs encoder and decoder')
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax

    def plot_edge_weights_histogram(self, bins=200, save_path=None):
        fig, axs = plt.subplots(2,2, figsize=(12,12))
#        axs[0,0].hist(self.grid_edge_weights, bins=bins, label='grid edge_weights', density=True)
#        axs[0,0].grid(ls='--')
#        axs[0,0].set_xlabel('edge weight')
#        axs[0,0].set_ylabel('count (normalized)')
#        axs[0,0].set_title('Grid')

        axs[1,0].hist(self.mesh_edge_weights, bins=bins, label = 'mesh edge weights', density=True)
        axs[1,0].grid(ls='--')
        axs[1,0].set_xlabel('edge weight')
        axs[1,0].set_ylabel('count (normalized)')
        axs[1,0].set_title('Mesh')

        axs[0,1].hist(self.encoder_edge_weights, bins=bins, label='encoder edge weights', density=True)
        axs[0,1].grid(ls='--')
        axs[0,1].set_xlabel('edge weight')
        axs[0,1].set_ylabel('count (normalized)')
        axs[0,1].set_title('Encoder')

        axs[1,1].hist(self.decoder_edge_weights, bins=bins, label='decoder edge weights', density=True)
        axs[1,1].grid(ls='--')
        axs[1,1].set_xlabel('edge weight')
        axs[1,1].set_ylabel('count (normalized)')
        axs[1,1].set_title('Decoder')

        fig.suptitle('Normalized edge weights')
        if save_path is not None:
            fig.savefig(save_path)
        return fig, axs

    def plot_area_weights(self, xlim=(-180, 180), ylim=(-90,90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        c = ax.scatter(self.grid_lons, self.grid_lats, c = self.area_weights, vmin=0, vmax = np.max(self.area_weights), marker='.')
        fig.colorbar(c, ax=ax, label='area weight', shrink=0.7)
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax

    def plot_obs_area_weights(self, xlim=(-180, 180), ylim=(-90,90), save_path=None):
        fig, ax = plt.subplots(figsize=(12,6), subplot_kw=dict(projection=ccrs.PlateCarree()))
        ax.coastlines()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        c = ax.scatter(self.obs_lons, self.obs_lats, c = self.obs_area_weights, marker='.')
        fig.colorbar(c, ax=ax, label='obs area weight', shrink=0.7)
        if save_path is not None:
            fig.savefig(save_path)
        return fig, ax   
    
        
class GraphInspector_for_anemoi_graphs(GraphInspector):
    def __init__(self, graph_data, grid_key = 'grid', hidden_key = 'hidden', coords_key='coords', obs_key=None, verbose = True) -> None:           
        super().__init__(
            graph_data = graph_data,
            grid_key=grid_key,
            hidden_key=hidden_key,
            coords_key=coords_key,
            verbose=verbose,
            obs_key=obs_key
        )
    
    @property
    def area_weights(self):
        return (self.graph_data[self.grid_key]["area_weight"][:,0]).numpy()
    
    @property
    def mesh_edge_weights(self):
        return (self.graph_data[self.h2h_key]["edge_length"][:,0]).numpy()
    
    @property
    def encoder_edge_weights(self):
        return (self.graph_data[self.e2h_key]["edge_length"][:,0]).numpy()
    
    @property
    def decoder_edge_weights(self):
        return (self.graph_data[self.h2e_key]["edge_length"][:,0]).numpy()


    

    



