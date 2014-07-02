
# project name (generate executable with this name)
TARGET   = UAPDFSyst

# COMPILER
CXX      = g++ 
CFLAGS   = -g -Wall

# LHAPDF
LHAPDF_INCDIR  = `lhapdf-config --incdir`
LHAPDF_LIBDIR  = `lhapdf-config --libdir`

# ROOT
ROOT_INCDIR    = `root-config --incdir`
ROOT_LIBS      = `root-config --libs`
ROOT_TPLIB     = -lTreePlayer
ROOT_GLIBS     = `root-config --glibs`
ROOT_CFLAGS    = `root-config --cflags`

# PROJECT
INCDIR   = `pwd`"/includes"

$(TARGET): 
	$(CXX) $(CFLAGS) \
	-I$(LHAPDF_INCDIR) -L$(LHAPDF_LIBDIR) -lLHAPDF \
	-I$(ROOT_INCDIR) $(ROOT_LIBS) $(ROOT_TPLIB) $(ROOT_GLIBS) $(ROOT_CFLAGS) \
	-I$(INCDIR) \
	$@.C -o $@.exe

