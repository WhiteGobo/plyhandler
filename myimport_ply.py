from .datacontainer import *

class InvalidPlyFormat( Exception ):
    pass

def get_header_and_data_from_file( filename ):
    headerbuffer = []
    fileposition = 0
    with open( filename, "r", errors='surrogateescape' ) as plyfile:
        if plyfile.readline().split()[0] != "ply":
            raise InvalidPlyFormat("File doesnt seem to be in plyformat")
        plyfile.seek( fileposition )
        headerended = False
        while not headerended:
            nextline = plyfile.readline()
            if len( nextline ) == 0:
                raise InvalidPlyFormat("Reached end of file "\
                                        "before header ended")
            nextline = nextline.split() #"\n" become [], so len(nl)>0 is needed
            if len( nextline ) > 0:
                headerbuffer.append( nextline )
                headerended = (nextline[0] == "end_header")
        del( nextline, headerended )
        fileposition = plyfile.tell()

    if headerbuffer[1][0] == "format" and headerbuffer[1][1] \
                    in ("ascii", "binary_little_endian", "binary_big_endian"):
        fileformat =  headerbuffer[1][1]
    else:
        raise InvalidPlyFormat( "couldnt get format from plyfile" )

    headerbuffer = [ line for line in headerbuffer if line[0] != 'comment' ]
    for line in headerbuffer:
        if line[0] not in ("ply", "format", "element", \
                            "property", "end_header"):
            raise InvalidPlyFormat(f"Cant interpret headerline: '{line}'")

    if fileformat == "ascii":
        with open( filename, "r" ) as plyfile:
            plyfile.seek( fileposition )
            mylines = plyfile.readlines()
            data = [ line for line in mylines if len( line ) > 0 ]
    elif fileformat in ("binary_little_endian", "binary_big_endian"):
        with open( filename, "rb" ) as plyfile:
            plyfile.seek( fileposition )
            data = plyfile.readlines()
    return headerbuffer, data, fileformat
