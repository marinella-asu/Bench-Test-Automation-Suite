import ctypes as ct

def cstr(self, a_string, encoding='utf-8'):
    a_string = (str(a_string)).encode(encoding)
    return ct.create_string_buffer(a_string)
