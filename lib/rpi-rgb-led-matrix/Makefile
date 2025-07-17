CXXFLAGS=-Wall -O3 -g -fno-strict-aliasing
BINARIES=led-matrix minimal-example text-example rgbmatrix.so

# Where our library resides. It is split between includes and the binary
# library in lib
RGB_INCDIR=include
RGB_LIBDIR=lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a
# Detect OS and adjust flags accordingly
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lm -lpthread
else
    LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lrt -lm -lpthread
endif

all : $(BINARIES)

$(RGB_LIBRARY):
	$(MAKE) -C $(RGB_LIBDIR)

led-matrix : demo-main.o $(RGB_LIBRARY)
	$(CXX) $(CXXFLAGS) demo-main.o -o $@ $(LDFLAGS)

minimal-example : minimal-example.o $(RGB_LIBRARY)
	$(CXX) $(CXXFLAGS) minimal-example.o -o $@ $(LDFLAGS)

text-example : text-example.o $(RGB_LIBRARY)
	$(CXX) $(CXXFLAGS) text-example.o -o $@ $(LDFLAGS)

# Python module - detect Python version and include paths
PYTHON_CONFIG := $(shell which python2.7-config || which python-config || echo "python-config")
PYTHON_INCLUDES := $(shell $(PYTHON_CONFIG) --includes 2>/dev/null || echo "-I/usr/include/python2.7")
PYTHON_LDFLAGS := $(shell $(PYTHON_CONFIG) --ldflags 2>/dev/null || echo "-lpython2.7")

rgbmatrix.so: rgbmatrix.o $(RGB_LIBRARY)
	$(CXX) -s -shared -lstdc++ -Wl,-soname,librgbmatrix.so $(PYTHON_LDFLAGS) -o $@ $< $(LDFLAGS)

%.o : %.cc
	$(CXX) -I$(RGB_INCDIR) $(CXXFLAGS) -DADAFRUIT_RGBMATRIX_HAT -c -o $@ $<

# Special rule for Python module compilation
rgbmatrix.o : rgbmatrix.cc
	$(CXX) -I$(RGB_INCDIR) $(PYTHON_INCLUDES) $(CXXFLAGS) -DADAFRUIT_RGBMATRIX_HAT -fPIC -c -o $@ $<

clean:
	rm -f *.o $(OBJECTS) $(BINARIES)
	$(MAKE) -C lib clean
