#include <Python.h>
#include <netinet/in.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>

unsigned char* pData;
unsigned char* currP;
int sizeData;
int bytelen;

static PyObject *fileError;

static PyObject *
startRead(PyObject *self, PyObject *args) // map file to memory
{
	char* idxFile;
	if(!PyArg_ParseTuple(args, "si", &idxFile, &bytelen))
		return NULL; // appropriate exception,  is given by PyArg_ParseTuple
	int fd;
	fd=open(idxFile, O_RDONLY, (mode_t)0400);
	if(fd==-1) {
		PyErr_SetString(fileError, "Couldn't read the specified file");
		return NULL;
	}
	
	sizeData=lseek(fd, 0, SEEK_END);
	lseek(fd, 0, SEEK_SET);

	pData=mmap(NULL, sizeData, PROT_READ, MAP_PRIVATE, fd, 0);
	currP=pData;
	if(pData==-1) {
		PyErr_SetString(fileError, "Couldn't load the specified file into memory");
		return NULL;
	}

	return Py_BuildValue("s", NULL);
} 

static PyObject *
nextRecord(PyObject *self, PyObject *args) // next string (null terminated), 2 ints
{
	if(currP>=pData+sizeData) {
		PyErr_SetString(PyExc_StopIteration, "EOF");
		return NULL;
	}

	if(!PyArg_ParseTuple(args, ""))
		return NULL;
	
	char str[260]; // max length is 256
	long long offset=0, size=0;
	int strsize=0;
	while(*currP!=0) {
		str[strsize]=*currP;
		currP++;
		strsize++;
	}
	str[strsize]=0;

	currP++;
	unsigned char* tmp;
	int i=0;
	while(i<bytelen) {
		tmp=currP;
		offset+=(*tmp)*pow(2, (bytelen-i-1)*8);
		i++;
		currP++;
	}
	i=0;
	while(i<4) {
		tmp=currP;
		size+=(*tmp)*pow(2, (3-i)*8);
		i++;
		currP++;
	}
	
	return Py_BuildValue("(sii)", str, offset, size); // idx in networkbyteorder
} 

static PyObject *
stopRead(PyObject *self, PyObject *args) // release sources
{
	if(munmap(pData, sizeData)==-1) {
		PyErr_SetString(fileError, "Couldn't deallocate memory");
		return NULL;
	}
	return Py_BuildValue("s", NULL);
} 

static PyMethodDef readidxMethods[] = {
    {"startRead",  startRead, METH_VARARGS, "Start reading idx file."},
    {"nextRecord",  nextRecord, METH_VARARGS, "Get next tuple of data (name, index, size)."},
    {"stopRead",  stopRead, METH_VARARGS, "Release allocated variables."},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef readidxModule = {
	PyModuleDef_HEAD_INIT,
	"readidx",	/* name of module */
	NULL,		/* module documentation, may be NULL */
    -1,			/* size of per-interpreter state of the module,
					or -1 if the module keeps state in global variables. */
	readidxMethods	
};

PyMODINIT_FUNC
PyInit_readidx(void)
{
	PyObject* r=PyModule_Create(&readidxModule);
	fileError=PyErr_NewException("readidx.fileError", NULL, NULL);
	Py_INCREF(fileError);
	PyModule_AddObject(r, "fileError", fileError);
	return r;
}

