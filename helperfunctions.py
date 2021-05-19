def get_dataarray_as_strings( plyobject, elementname, propertyname, \
                                                            encoding="utf8" ):
    stringdata = plyobject.get_dataarray( elementname, propertyname )
    return [ str( single, encoding="utf8" ) for single in stringdata ]

def strings_to_uchararrays( stringlist, encoding="utf8" ):
    return [ bytes( single, encoding="utf8" ) for single in stringlist ]
