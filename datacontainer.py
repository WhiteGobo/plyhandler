import struct
import itertools
from .myexport_ply import create_header, \
                        create_data_ascii, \
                        create_data_binary_little_endian, \
                        create_data_binary_big_endian
from .myimport_ply import get_header_and_data_from_file
from .myimport_ply import InvalidPlyFormat


class ObjectSpec:
    def __init__( self, elementspec_dict ):
        self._element_to_propertylist = dict( elementspec_dict )
        self._elementspec = dict( elementspec_dict )
        self.properties = { k.name: v for k, v in elementspec_dict.items() }

    @classmethod
    def from_arrays( cls, elemtripel ):
        """
        :param elemtripel: tripel of 
                elementname,
                list of description of properties,
                and dataarrays one for each property
            example: 
                (
                "vertex", 
                [("int","x"),("int","y")], 
                [(1,2,3),(4,5,6)]
                )
        """
        reform = lambda elemname, properties_multidata, elemdata: \
                            (elemname, properties_multidata, \
                                    list(itertools.zip_longest( *elemdata )))
        datapoint_elemtripel = [ reform( x,y,z ) for x,y,z in elemtripel ]
        return cls.from_datapoints( datapoint_elemtripel )

    @classmethod
    def from_datapoints( cls, elemtripel ):
        """
        Same as from_arrays but with datapoints instead of arrays
        example:
                (
                "vertex", 
                [("int","x"),("int","y")], 
                [(1,4), (2,5), (3,6)]
                )
        """
        elements = dict()
        elem_with_data = []
        for elemname, properties_multidata, elemdata in elemtripel:
            elemnumber = len( elemdata )
            newelem = _element( elemname, elemnumber )
            tmplist = list()
            elements[ newelem ] = tmplist
            for propdata in properties_multidata:
                datatype = propdata[0]
                if datatype == "list":
                    listelem_type, listlength_type, name = propdata[1:]
                    tmp = _property( name, datatype, listelem_type, \
                                                        listlength_type )
                else:
                    name = propdata[1]
                    tmp = _property( name, datatype )
                tmplist.append( tmp )
            elem_with_data.append( (newelem, elemdata) )

        myobj = cls( elements )
        for elem, elemdata in elem_with_data:
            for datapoint in elemdata:
                elem.append( datapoint )
        return myobj

    @classmethod
    def from_fileheader( cls, header ):
        elementlines = []
        for line in header:
            if line[0] == "element":
                lastelementlist = list()
                elementlines.append( (line[1:], lastelementlist) )
            elif line[0] == "property":
                try:
                    lastelementlist.append( line[1:] )
                except UnboundLocalError as err:
                    raise InvalidPlyFormat("first property before element") \
                                                                    from err

        elements = dict()
        for elemdata, properties_multidata in elementlines:
            elem_name, elem_number = elemdata[0], int( elemdata[1] )
            newelem = _element( elem_name, elem_number )
            tmplist = list()
            elements[ newelem ] = tmplist
            for propdata in properties_multidata:
                datatype = propdata[0]
                if datatype == "list":
                    listelem_type, listlength_type, name = propdata[1:]
                    tmp = _property( name, datatype, listelem_type, \
                                                        listlength_type )
                else:
                    name = propdata[1]
                    tmp = _property( name, datatype )
                tmplist.append( tmp )
        return cls( elements )


    @classmethod
    def load_from_file( cls, filename ):
        header, data, fileformat = get_header_and_data_from_file( filename )
        mydata = cls.from_fileheader( header )
        filling = { \
                "ascii": mydata._fill_with_asciidata, \
                "binary_little_endian": mydata._fill_with_little_endian_data, \
                "binary_big_endian": mydata._fill_with_big_endian_data, \
                }
        filling[ fileformat ]( data )
        return mydata

    def save_to_file( self, filename, dataformat=None, comments=[] ):
        if dataformat == None:
            dataformat = self.format
        datacreationlib = { \
                "ascii": create_data_ascii, \
                "binary_little_endian": create_data_binary_little_endian, \
                "binary_big_endian": create_data_binary_big_endian, \
                }
        header = create_header( self, dataformat, comments )
        if header[-1] != "\n":
            header = header + "\n"
        data = datacreationlib[ dataformat ]( self )
        with open( filename, "w" ) as plyfile:
            plyfile.write( header )
            currentpos = plyfile.tell()
        writeformat_data = {"ascii":"a", "binary_little_endian": "ab", \
                            "binary_big_endian": "ab" }[ dataformat ]
        with open( filename, writeformat_data ) as plyfile:
            plyfile.seek( currentpos )
            plyfile.write( data )

    def _get_elementname_to_propertylist( self ):
        return self.properties
    elementname_to_propertylist = property( \
                                    fget=_get_elementname_to_propertylist )

    def _get_elements( self ):
        return self._elementspec.keys()
    elements = property( fget=_get_elements )

    def _get_nameelement_dictionary( self ):
        return { elem.name: elem for elem in self.elements }
    _name_to_element = property( fget=_get_nameelement_dictionary )

    def _get_data( self ):
        return self._name_to_element
    data = property( fget=_get_data )

    def get_dataarray( self, elementname, propertyname ):
        asd = self.get_filtered_data( elementname, [propertyname] )
        return [ i[0] for i in asd ]

    def get_filtered_data( self, elementname, propertynames ):
        elemdata = self._name_to_element[ elementname ]
        proplist = self.elementname_to_propertylist[ elementname ]
        name_to_index = { prop.name:i for i, prop in enumerate(proplist) }
        elemlist = [ name_to_index[propname] for propname in propertynames]
        myfilter = lambda tup: tuple( tup[i] for i in elemlist )
        return [ myfilter(data) for data in elemdata ]

    def _fill_with_asciidata( self, data ):
        data = iter( data )
        for elem in self.elements:
            for n in range(elem.number):
                tmp = data.__next__()
                nextline = iter( tmp.split() )
                singledata = []
                for prop in self.properties[ elem.name ]:
                    if prop.datatype == "list":
                        tmplist = []
                        listlength = int( nextline.__next__() )
                        for i in range( listlength ):
                            if prop.listelem_type in ("float", "double"):
                                tmplist.append( float(nextline.__next__()) )
                            elif prop.listelem_type in ("char","uchar","short",\
                                                    "ushort", "int", "uint"):
                                tmplist.append( int( nextline.__next__()))
                        singledata.append( tmplist )
                        del( tmplist )
                    if prop.datatype in ("float", "double"):
                        singledata.append( float( nextline.__next__()) )
                    elif prop.datatype in ("char", "uchar", "short", \
                                                    "ushort", "int", "uint"):
                        singledata.append( int( nextline.__next__()))
                elem.append( singledata )


    def _fill_with_binary_data( self, data, byteorder="little" ):
        byteorder = {   '<':'<', "little":'<', "little_endian":'<', \
                        '>':'>', "big":'>', "big_endian":'>' \
                        }[ byteorder ]
        data = iter( data )
        typelength = { "char":1, "uchar":1, "short":2, "ushort":2, \
                    "int":4, "uint":4, "float":4, "double":8, }
        getnext = lambda nextbyte, datatype: bytes( nextbyte.__next__() \
                                        for i in range(typelength[datatype]))
        nextbyte = iter( data.__next__() )
        for elem in self.elements:
            for n in range(elem.number):
                singledata = []
                for prop in self.properties[ elem.name ]:
                    if prop.datatype == "list":
                        tmplist = []
                        data = getnext( nextbyte, prop.listlength_type )
                        listlength, = _littleunpack( data, prop.listlength_type)
                        for i in range( listlength ):
                            data = getnext( nextbyte, prop.listelem_type )
                            tmplist.extend( _littleunpack( data, \
                                                        prop.listelem_type ))
                        singledata.append( tmplist )
                        del( tmplist )
                    else:
                        data = getnext( nextbyte, prop.datatype )
                        singledata.extend( _littleunpack( data, prop.datatype ))
                elem.append( singledata )

    def _fill_with_little_endian_data( self, data ):
        return self._fill_with_binary_data( data, "little" )

    def _fill_with_big_endian_data( self, data ):
        return self._fill_with_binary_data( data, "big" )

class _element( list ):
    def __init__( self, name, number ):
        if all(( type(number)==int, number >= 0 )):
            self.name = name
            self.number = number
        else:
            raise Exception()
    def __hash__( self ):
        return super( list ).__hash__()
    def __repr__( self ):
        return f"Element_{self.name}"

class _property():
    def __init__( self, name, datatype, listelem_type=None, \
                                            listlength_type=None ):
        if any((\
                datatype == "list" and listelem_type is not None \
                                            and listlength_type is not None,
                datatype in ( "char", "uchar", "short", "ushort", \
                            "int", "uint", "float", "double" ) \
                                            and listelem_type is None \
                                            and listlength_type is None,
                )):
            self.name = name
            self.datatype = datatype
            self.listelem_type = listelem_type
            self.listlength_type = listlength_type
        else:
            raise Exception( f"Oops something went wrong, {name}, {datatype},"\
                            + f" {listelem_type}, {listlength_type}" )

def _littleunpack( databuffer, dataformat ):
    formatchar = { "char":'b', "uchar":'B', "short":'h', "ushort":'H', \
                    "int":'i', "uint":'I', "float":'f', "double":'d', }
    return struct.unpack( '<' + formatchar[dataformat], databuffer )

def _bigunpack( data, dataformat ):
    formatchar = { "char":'b', "uchar":'B', "short":'h', "ushort":'H', \
                    "int":'i', "uint":'I', "float":'f', "double":'d', }
    return struct.unpack( '>' + formatchar[dataformat], databuffer )

def _littlepack( databuffer, dataformat ):
    formatchar = { "char":'b', "uchar":'B', "short":'h', "ushort":'H', \
                    "int":'i', "uint":'I', "float":'f', "double":'d', }
    return struct.pack( '<' + formatchar[dataformat], databuffer )

def _bigpack( data, dataformat ):
    formatchar = { "char":'b', "uchar":'B', "short":'h', "ushort":'H', \
                    "int":'i', "uint":'I', "float":'f', "double":'d', }
    return struct.pack( '>' + formatchar[dataformat], databuffer )
