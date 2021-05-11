from .myimport_ply import load_ply_obj_from_filename
from scipy.spatial import Delaunay
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
import numpy as np
import itertools


def create_surfacemap( surfinter, ulength, vlength ):
    umin, umax = 0, ulength
    vmin, vmax = 0, vlength

    nu, nv = ulength+1, vlength+1
    xyzmatrix = []
    #u_array = np.linspace(umin, umax, nu)
    #v_array = np.linspace(vmin, vmax, nv)
    u_array = np.linspace(0,1, ulength)
    v_array = np.linspace(0,1,vlength )
    for u in u_array:
        current_line = []
        xyzmatrix.append( current_line )
        for v in v_array:
            current_line.append( surfinter( u, v ) )
    xyzmatrix = np.stack( xyzmatrix )
    xyzmatrix = xyzmatrix

    asd = surfacemap( xyzmatrix, u_array, v_array )
    #for i, u in enumerate( u_array ):
    #    for j, v in enumerate( v_array ):
    #        print( i,j, np.array( asd.pos( u,v ) )- np.array(xyzmatrix[i][j]) )

    return asd



class surfacemap():
    def __init__( self, xyzmatrix, u_array=None, v_array=None ):
        if u_array == None:
            u_array = np.linspace( 0,1, np.array(xyzmatrix).shape[0] )
        if v_array == None:
            v_array = np.linspace( 0,1, np.array(xyzmatrix).shape[1] )
        #u_m, v_m = np.meshgrid( u_array, v_array )
        #uv = np.ndarray( (len(u_array), len(v_array),2) )

        xyz = np.array( xyzmatrix )
        x = xyz[:,:,0]
        y = xyz[:,:,1]
        z = xyz[:,:,2]
        self.mapx = create_mapping_device_fromgrid( u_array, v_array, x )
        self.mapy = create_mapping_device_fromgrid( u_array, v_array, y )
        self.mapz = create_mapping_device_fromgrid( u_array, v_array, z )
        self.umin, self.umax = min(u_array), max(u_array)
        self.vmin, self.vmax = min(v_array), max(v_array)

        dxdu, dxdv, dydu, dydv, dzdu, dzdv = self._calc_grads( xyz, \
                                                    len(u_array), len(v_array))
        self.mapdxdu = create_mapping_device_fromgrid( u_array, v_array, dxdu )
        self.mapdxdv = create_mapping_device_fromgrid( u_array, v_array, dxdv )
        self.mapdydu = create_mapping_device_fromgrid( u_array, v_array, dydu )
        self.mapdydv = create_mapping_device_fromgrid( u_array, v_array, dydv )
        self.mapdzdu = create_mapping_device_fromgrid( u_array, v_array, dzdu )
        self.mapdzdv = create_mapping_device_fromgrid( u_array, v_array, dzdv )
        self.maxdistance = self.calc_max_distance_with_grad( x, y, z, u_array, v_array )


    def __call__( self, u, v ):
        x = self.mapx( u, v )
        y = self.mapy( u, v )
        z = self.mapz( u, v )
        return x, y, z

    def singularmaps( self ):
        return self.mapx, self.mapy, self.mapz

    def grad_realtomap( self ):
        surf_gradhvtoxyz_tuple = self.mapdxdu, self.mapdxdv, self.mapdydu, \
                                self.mapdydv, self.mapdzdu, self.mapdzdv
        return surf_gradhvtoxyz_tuple

    def calc_max_distance_with_grad( self, data_x, data_y, data_z, \
                                                        u_array, v_array ):
        deltau = min( abs(u_array[i]-u_array[i+1]) \
                        for i in range(len(u_array)-1))
        deltav = min( abs(v_array[i]-v_array[i+1]) \
                        for i in range(len(v_array)-1))
        mydelta = min( deltau, deltav )
        maximal_error = 0.1

        max_divgrad_hv = 0
        for data in ( data_x, data_y, data_z ):
            grad1, grad2 = np.gradient( data )
            for grad in (grad2, grad2):
                divgrad1, divgrad2 = np.gradient( grad )
                for i in itertools.chain( *divgrad1, *divgrad2 ):
                    max_divgrad_hv = max( max_divgrad_hv, np.abs( i ) )

        return np.sqrt( maximal_error/max_divgrad_hv )*mydelta

        
    def grad_maxdistance( self ):
        return self.maxdistance


    def pos( self, u, v ):
        x = self.mapx( u, v )
        y = self.mapy( u, v )
        z = self.mapz( u, v )
        return x, y, z
    def pos_array( self, u, v ):
        return np.array( self.pos(u,v) )

    def grad( self, u, v ):
        dxdu = self.mapdxdu( u, v )
        dxdv = self.mapdxdv( u, v )
        dydu = self.mapdydu( u, v )
        dydv = self.mapdydv( u, v )
        dzdu = self.mapdzdu( u, v )
        dzdv = self.mapdzdv( u, v )
        return dxdu, dxdv, dydu, dydv, dzdu, dzdv
    def grad_array( self, u, v ):
        dxdu, dxdv, dydu, dydv, dzdu, dzdv = self.grad_array( u, v )
        return np.array(((dxdu, dxdv),(dydu, dydv),(dzdu,dzdv)))

    def _calc_grads( self, xyz, ulength, vlength ):
        x = xyz[:,:,0]
        y = xyz[:,:,1]
        z = xyz[:,:,2]
        ulength = ulength * -0.01
        vlength = vlength * -0.01

        Dx = np.gradient( x )
        Dy = np.gradient( y )
        Dz = np.gradient( z )
        dxdu, dxdv = Dx[0]*ulength, Dx[1]*vlength
        dydu, dydv = Dy[0]*ulength, Dy[1]*vlength
        dzdu, dzdv = Dz[0]*ulength, Dz[1]*vlength
        return dxdu, dxdv, dydu, dydv, dzdu, dzdv


def generate_surfaceinterpolator( vertexpositions, st_coordinates ):
    delaunay_triang = Delaunay( st_coordinates )
    xyz_as_uvmap = LinearNDInterpolator( delaunay_triang, vertexpositions)
    return xyz_as_uvmap



def create_mapping_device_fromgrid( u_array, v_array, curveddata_z ):
    if any( u_array[i] > u_array[i+1] for i in range(len(u_array)-1) ) \
            and any( v_array[i] > v_array[i+1] for i in range(len(v_array)-1)):
        raise Exception( "metrix-array u and v must be increasing monotonously")
    umin, umax = u_array[0], u_array[-1]
    vmin, vmax = v_array[0], v_array[-1]
    ulength = len( u_array )
    vlength = len( v_array )
    urange, vrange = umax-umin, vmax-vmin
    delta_per_row = vrange+1

    zused = extend_matrix_right( curveddata_z )
    zused = extend_matrix_down( zused )
    metrix_uv = np.array( v_array)
    metrix_uv.resize((1,len(v_array)+1))
    metrix_uv[0][-1] = metrix_uv[0][-2] + 0.9
    metrix_uv = metrix_uv * np.ones((len(u_array)+1,1))
    for i in range( len(metrix_uv)):
        metrix_uv[i] += i*delta_per_row

    ss = metrix_uv.size
    metrix_uv = np.array( metrix_uv ).reshape( ss )
    zused = np.array( zused ).reshape( ss )

    
    def griddata_z( posu, posv ):
        posu = np.interp( posu, u_array, np.arange( ulength ))
        factor = np.remainder( posu, 1 )
        s_lower = posv + delta_per_row*(posu - factor)
        s_higher = s_lower + delta_per_row

        z1 = np.interp( s_lower, metrix_uv, zused )
        z2 = np.interp( s_higher, metrix_uv, zused )
        z = factor * (z2 - z1) + z1
        return z
    return griddata_z
        
def extend_matrix_down( mymatrix ):
    mymatrix = np.append( mymatrix, mymatrix[:,-1:], 1 )
    return mymatrix

def extend_matrix_right( mymatrix ):
    mymatrix = np.append( mymatrix, mymatrix[-1:,:], 0 )
    return mymatrix
