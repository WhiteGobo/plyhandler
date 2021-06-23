import itertools

def create_header( ply_object, myformat, comments, spacer=" ", version=(1,0) ):
    headerparts = []
    headerparts.append( "ply" )
    headerparts.append( spacer.join(( "format",myformat,"%d.%d"%version )) )
    for com in comments:
        headerparts.append( spacer.join(("comment", com)))
    for elem in ply_object.elements:
        headerparts.append( spacer.join(( "element", elem.name, \
                                                    str(elem.number) )))
        for prop in ply_object.properties[ elem.name ]:
            if prop.datatype == "list":
                headerparts.append( spacer.join(("property", prop.datatype, \
                                    prop.listlength_type, prop.listelem_type,\
                                    prop.name )))
            else:
                headerparts.append( spacer.join(("property", prop.datatype, \
                                    prop.name)) )
    headerparts.append( "end_header" )
    return "\n".join(headerparts) + "\n"


formatter = { "char":'%d', "uchar":'%d', "short":'%d', "ushort":'%d', \
                    "int":'%d', "uint":'%d', "float":'%e', "double":'%e', }
def create_data_ascii( ply_object, spacer=" " ):
    from .datacontainer import BrokenPlyObject
    databuffer = []
    formatter = { "char":'%d', "uchar":'%d', "short":'%d', "ushort":'%d', \
                    "int":'%d', "uint":'%d', "float":'%e', "double":'%e', }
    for elem in ply_object.elements:
        lineformatter = []
        for prop in ply_object.properties[ elem.name ]:
            if prop.datatype == "list":
                foo = create_listformatter( prop.listelem_type, \
                                            prop.listlength_type,
                                            spacer )
                lineformatter.append( foo )
            else:
                usedformatter = formatter[ prop.datatype ]
                def asd( x ):
                    return usedformatter%x
                lineformatter.append( asd )
                #lineformatter.append( lambda x: tmp%x )
                #del( asd, tmp )
        try:
            for line in ply_object.data[elem.name]:
                line = list( line ) #Im not sure sometimes this does help???
                formattedline = [ formfoo( single ) \
                                for single, formfoo \
                                in zip( line,lineformatter ) \
                                ]
                databuffer.append( spacer.join( formattedline ) )
        except TypeError as err:
            raise BrokenPlyObject( \
                        f"couldnt format data of element {elem.name}") from err
    return "\n".join( databuffer )

def create_listformatter( listelem_type, listlength_type, spacer ):
    elemf = formatter[ listelem_type ]
    listf = formatter[ listlength_type ]
    def foo( mylist ):
        return spacer.join(( \
                            listf%len(mylist), \
                            *( elemf%i for i in mylist ) \
                            ))
    return foo

def create_data_binary( ply_object, dataformat:str ):
    import struct
    formatchar = { "char":'b', "uchar":'B', "short":'h', "ushort":'H', \
                    "int":'i', "uint":'I', "float":'f', "double":'d', }
    databuffer = bytearray()
    for elem in ply_object.elements:
        lineformatter = []
        for prop in ply_object.properties[ elem.name ]:
            if prop.datatype == "list":
                elemf = formatchar[ prop.listelem_type ]
                listf = formatchar[ prop.listlength_type ]
                def foo( mylist ):
                    return b''.join((
                            struct.pack( dataformat + listf, len( mylist )), \
                            *( struct.pack( dataformat + elemf, x) \
                            for x in mylist ), \
                            ))
                lineformatter.append( foo )
            else:
                def asd( x ):
                    return struct.pack( dataformat \
                                        + formatchar[ prop.datatype ], x )
                lineformatter.append( asd )
        for line in ply_object.data[elem.name]:
            for single, formfoo in itertools.zip_longest( line, lineformatter ):
                databuffer.extend( formfoo( single ) )
    return databuffer

def create_data_binary_little_endian( ply_object ):
    return create_data_binary( ply_object, dataformat="<" )

def create_data_binary_big_endian( ply_object ):
    return create_data_binary( ply_object, dataformat=">" )
