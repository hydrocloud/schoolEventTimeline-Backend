import ctypes

utils = ctypes.CDLL("./utils.so")
utils.zhixue_pw_encode.argtypes = [ctypes.c_char_p]
utils.zhixue_pw_encode.restype = ctypes.c_char_p

utils.init()

print utils.zhixue_pw_encode("000000000000000")
print utils.zhixue_pw_encode("0000000000000000")
print utils.zhixue_pw_encode("00000000000000000")
print utils.zhixue_pw_encode("123456")

utils.free_memory()

