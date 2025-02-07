import ctypes as ct
def cstr( a_string, encoding='utf-8' ):
    return ct.create_string_buffer( bytes( a_string , encoding) )