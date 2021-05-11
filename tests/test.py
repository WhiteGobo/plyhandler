import unittest
from .. import main
import importlib.resources
from .. import tests as testsource

class test_asd( unittest.TestCase ):
    def test_asd( self ):
        with importlib.resources.path( testsource, "tmp.ply" ) as filepath:
            print( filepath )


if __name__ == "__main__":
    unittest.main()
