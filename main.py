import argparse
from .myimport_ply import load_ply_obj_from_filename
from .myexport_ply import export_plyfile
import numpy as np

def get_args():
    parser = argparse.ArgumentParser( description="" )
    parser.add_argument( "filename", type=str ) 
    args = parser.parse_args()
    return args.filename


def main( filename ):
    myobj = load_ply_obj_from_filename( filename )

    (uv_size,) = myobj["matrix"].get_filtered_data( "u","v" )
    (vertexpositions,) = myobj["matrix"].get_filtered_data( "x", "y", "z" )

    mydata = np.ndarray(( uv_size[0]*uv_size[1], 3 ))
    mydata[:,0] = vertexpositions[0]
    mydata[:,1] = vertexpositions[1]
    mydata[:,2] = vertexpositions[2]
    mydata = mydata.reshape( (*uv_size, 3) )

    from .create_surfacemap import surfacemap
    #u_array = np.linspace( 0,1, uv_size[0] )
    #v_array = np.linspace( 0,1, uv_size[1] )
    mysurface = surfacemap( mydata )#, u_array, v_array )

    return mysurface


if __name__=="__main__":
    filename = get_args()
    mysurfacemap = main( filename )
    umax, vmax = 10, 10
    q = np.ndarray((umax, vmax, 3))
    for i, u in enumerate( np.linspace( 0, 1, umax )):
        for j, v in enumerate( np.linspace( 0, 1, vmax )):
            q[i,j] = mysurfacemap( u, v )

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot( 111, projection='3d' )
    ax.scatter( q[:,:,0], q[:,:,1], q[:,:,2] )
    plt.show()

