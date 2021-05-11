import unittest
from .. import main
import importlib.resources
from .. import tests as testsource
from ..datacontainer import plycontainer_from_arrays
from ..myimport_ply import load_ply_obj_from_filename
from ..myexport_ply import export_plyfile
import tempfile
import os.path
import numpy as np

class test_asd( unittest.TestCase ):
    def test_load_and_save_ascii( self ):
        with importlib.resources.path( testsource, "tmp.ply" ) as filepath:
            myobj = load_ply_obj_from_filename( filepath )
        vertexpositions = myobj["vertex"].get_filtered_data("x", "y", "z")
        self.assertEqual( tuple(vertexpositions), testA )
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "surfmap.ply" )
            export_plyfile( myfilepath, myobj, "ascii" )
            myobj2 = load_ply_obj_from_filename( myfilepath )
            vertexpositions2 = myobj["vertex"].get_filtered_data("x", "y", "z")
            self.assertEqual( vertexpositions, vertexpositions )

    def test_create_dataobject( self ):
        vertexpipeline = ( \
                            ( b"float", b"x" ), \
                            ( b"float", b"y" ), \
                            ( b"float", b"z" ), \
                            )
        facespipeline = ((b"list", b"uchar", b"uint", b"vertex_indices" ), )
        vert = np.array( testA ).T
        faces = (np.array( testB ),)
        myobj = plycontainer_from_arrays( [\
                            ("vertex", vertexpipeline, vert ), \
                            ("faces", facespipeline, faces ), \
                            ])
        with tempfile.TemporaryDirectory() as tmpdir:
            myfilepath = os.path.join( tmpdir, "tmp.ply" )
            export_plyfile( myfilepath , myobj, "ascii" )
            myobj2 = load_ply_obj_from_filename( myfilepath )
        vertexpositions = myobj2["vertex"].get_filtered_data("x", "y", "z")
        self.assertEqual( tuple(vertexpositions), testA )

testA = tuple( [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 1.0), \
            (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), \
            (1.0, 1.0, 1.0), (1.0, 1.0, 0.0)] )
testB = [ (0, 1, 2, 3), (7, 6, 5, 4), \
            (0, 4, 5, 1), (1, 5, 6, 2),\
            (2, 6, 7, 3), (3, 7, 4, 0) ]

if __name__ == "__main__":
    unittest.main()
