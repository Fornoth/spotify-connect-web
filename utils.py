from connect_ffi import ffi, lib

def get_zeroconf_vars():
    zeroconf_vars = ffi.new('SpZeroConfVars *')
    lib.SpZeroConfGetVars(zeroconf_vars)
    return convert_to_python(zeroconf_vars[0])

def print_zeroconf_vars():
    zeroconf_vars = get_zeroconf_vars()

    print "public key: {}".format(zeroconf_vars['publicKey'])
    print "device id: {}".format(zeroconf_vars['deviceId'])
    print "remote name: {}".format(zeroconf_vars['remoteName'])
    print "account req: {}".format(zeroconf_vars['accountReq'])
    print "device type: {}".format(zeroconf_vars['deviceType'])

def get_metadata():
    metadata = ffi.new('SpMetadata *')
    lib.SpGetMetadata(metadata, 0)
    return convert_to_python(metadata[0])

def get_image_url(uri):
     image_url = ffi.new('char[512]')
     #TODO: Change back to 640
     lib.SpGetMetadataImageURL(uri, lib.kSpImageSizeSmall, image_url, ffi.sizeof(image_url))
     return ffi.string(image_url)

#From https://gist.github.com/inactivist/4ef7058c2132fa16759d
def __convert_struct_field( s, fields ):
    for field,fieldtype in fields:
        if fieldtype.type.kind == 'primitive':
            yield (field,getattr( s, field ))
        else:
            yield (field, convert_to_python( getattr( s, field ) ))

#From https://gist.github.com/inactivist/4ef7058c2132fa16759d
def convert_to_python(s):
    type=ffi.typeof(s)
    if type.kind == 'struct':
        return dict(__convert_struct_field( s, type.fields ) )
    elif type.kind == 'array':
        if type.item.kind == 'primitive':
            if type.item.cname == 'char':
                return ffi.string(s)
            else:
                return [ s[i] for i in range(type.length) ]
        else:
            return [ convert_to_python(s[i]) for i in range(type.length) ]
    elif type.kind == 'primitive':
        return int(s)