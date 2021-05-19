import unittest
import importlib.resources
from .. import tests as testsource
#from ..datacontainer import plycontainer_from_arrays
#from ..myexport_ply import export_plyfile
import tempfile
import os.path
import numpy as np
from ..datacontainer import ObjectSpec

class test_asd( unittest.TestCase ):
    def test_load_and_save( self ):
        with importlib.resources.path( testsource, "tmp.ply" ) as filepath:
            myobj = ObjectSpec.load_from_file( filepath )
        vertexpositions = myobj.get_filtered_data("vertex",("x", "y", "z"))
        self.assertEqual( tuple(vertexpositions), testA )
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "surfmap.ply" )
            myobj.save_to_file( myfilepath, "ascii" )
            myobj2 = ObjectSpec.load_from_file( myfilepath )
            vertexpositions2 = myobj.get_filtered_data("vertex",("x", "y", "z"))
            self.assertEqual( vertexpositions, vertexpositions )
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "surfmap.ply" )
            myobj.save_to_file( myfilepath, "binary_little_endian" )
            myobj2 = ObjectSpec.load_from_file( myfilepath )
            vertexpositions2 = myobj.get_filtered_data("vertex",("x", "y", "z"))
            self.assertEqual( vertexpositions, vertexpositions )
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "surfmap.ply" )
            myobj.save_to_file( myfilepath, "binary_big_endian" )
            myobj2 = ObjectSpec.load_from_file( myfilepath )
            vertexpositions2 = myobj.get_filtered_data("vertex",("x", "y", "z"))
            self.assertEqual( vertexpositions, vertexpositions )

    def test_load_every_property_of_every_element( self ):
        with importlib.resources.path( testsource, "tmp.ply" ) as filepath:
            myobj = ObjectSpec.load_from_file( filepath )

        self.assertEqual( myobj.elements_and_propertynames, \
                    {'vertex': ['x', 'y', 'z', 'b'], \
                    'face': ['vertex_indices'], \
                    'cornerrectangle': ['leftup', 'rightup', \
                    'rightdown', 'leftdown']}
                    )
        testdings = { \
                ('vertex','x'): (0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0), \
                ('vertex','y'): (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0), \
                ('vertex','z'): (0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0), \
                #('vertex','m'): (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), \
                }
        for element, propertylist in myobj.elements_and_propertynames.items():
            for prop in propertylist:
                if (element, prop) in testdings.keys():
                    coordinatelist = myobj.get_dataarray( element, prop )
                    self.assertEqual( testdings[(element, prop)],\
                                        tuple( coordinatelist ) )
                elif element == 'face' and prop == 'vertex_indices':
                    facelist = myobj.get_dataarray( element, prop )
                    self.assertEqual( (0,1,2,3), tuple(facelist[0]) )
                else:
                    #check if no error occurs
                    myobj.get_dataarray( element, prop )

    def test_helperfunctions( self ):
        pass

    def test_create_dataobject( self ):
        vertexpipeline = ( \
                            ( "float", "x" ), \
                            ( "float", "y" ), \
                            ( "float", "z" ), \
                            )
        facespipeline = (("list", "uchar", "uint", "vertex_indices" ), )
        vert = np.array( testA ).T
        faces = (np.array( testB ),)
        myobj = ObjectSpec.from_arrays( [\
                            ("vertex", vertexpipeline, vert ), \
                            ("faces", facespipeline, faces ), \
                            ])
        vertexpositions = myobj.get_filtered_data("vertex", ("x", "y", "z"))
        self.assertEqual( tuple(vertexpositions), testA )
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "tmp.ply" )
            myobj.save_to_file( myfilepath, "ascii" )
            myobj2 = ObjectSpec.load_from_file( myfilepath )
        vertexpositions = myobj2.get_filtered_data("vertex", ("x", "y", "z"))
        self.assertEqual( tuple(vertexpositions), testA )

testA = tuple( [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 1.0), \
            (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), \
            (1.0, 1.0, 1.0), (1.0, 1.0, 0.0)] )
testB = [ (0, 1, 2, 3), (7, 6, 5, 4), \
            (0, 4, 5, 1), (1, 5, 6, 2),\
            (2, 6, 7, 3), (3, 7, 4, 0) ]

if __name__ == "__main__":
    unittest.main()
