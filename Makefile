CXXFLAGS := -O2 -fPIC -std=c++11

utils: utils.o
	$(CXX) -shared -o utils.so utils.o
	strip utils.so