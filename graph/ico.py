import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from icosphere import icosphere

def plot_icosahedron(refinement_level=0):
    """
    Generate and plot an icosahedron at a given refinement level.
    
    Args:
        refinement_level [int]: Refinement level of icosahedron.
    """


    from icosphere import icosphere
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors
    import mpl_toolkits.mplot3d 

    fig = plt.figure(figsize=(15, 10))

    for j, i in enumerate(refinement_level):
        vertices, faces = icosphere(nu=i)
        
        # basic mesh color, divided in 20 groups (one for each original face)
        jet = matplotlib.cm.tab20(np.linspace(0,1,20))
        jet = np.tile(jet[:,:3], (1, faces.shape[0]//20))
        jet = jet.reshape(faces.shape[0], 1, 3)
        jet[:, 0, 0] = 0.5
        jet[:, 0, 1] = 0.8
        jet[:, 0, 2] = 1

        # computing face shading intensity based on face normals  
        face_normals = np.cross(vertices[faces[:,1]]-vertices[faces[:,0]], 
                                vertices[faces[:,2]]-vertices[faces[:,0]])
        face_normals /= np.sqrt(np.sum(face_normals**2, axis=1, keepdims=True))               
        light_source = matplotlib.colors.LightSource(azdeg=60, altdeg=30)
        intensity = light_source.shade_normals(face_normals)

        # blending face colors and face shading intensity
        rgb = light_source.blend_hsv(rgb=jet, intensity=intensity.reshape(-1,1,1))   

        # adding alpha value, may be left out
        rgba = np.concatenate((rgb, 0.6*np.ones(shape=(rgb.shape[0],1,1))), axis=2) 

        # creating mesh with given face colors
        poly = mpl_toolkits.mplot3d.art3d.Poly3DCollection(vertices[faces])
        poly.set_facecolor(rgba.reshape(-1,4)) 
        poly.set_edgecolor('black')
        poly.set_linewidth(0.25)

        # and now -- visualization! 
        ax = fig.add_subplot(1,3,j+1,projection='3d')                  

        ax.add_collection3d(poly) 
            
        ax.set_xlim(-1,1)
        ax.set_ylim(-1,1)
        ax.set_zlim(-1,1)
        
        #ax.set_xticks([-1,0,1])
        #ax.set_yticks([-1,0,1])
        #ax.set_zticks([-1,0,1])
        ax.grid(False)
        plt.axis('off')
        
        ax.set_title(f'Refinement level={i-1}')
    plt.tight_layout()
    name = np.array(refinement_level) - np.array([1,1,1])
    plt.savefig(f'ico/ico_{name}', bbox_inches='tight')
    

if __name__ == '__main__':
    plot_icosahedron(refinement_level=[1,2,11])