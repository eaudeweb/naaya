/*
**
** TextIndexNG                The next generation TextIndex for Zope
**
** This software is governed by a license. See
** LICENSE.txt for the terms of this license.
**
*/

#include "Python.h"
#include <ctype.h>
#include "dict.h"

#ifndef min
#define min(a,b) ((a)<(b)?(a):(b))
#endif

/*
** struct for splitter
*/

typedef struct
{
    PyObject_HEAD
    PyObject *list;                    // list of splitted words
    hashtable *cache;                 
    unsigned char small_cache[256];
    int max_len;                       // maximum length of a word
    int single_chars;                  // allow single character words
    int casefolding;                   // mapping all to lower case
}
Splitter;


/*
** Node handling for hashtable.
** 
** We maintain a hashtable to store (key,value) pairs
** where the keys are the int value of a character or unicode 
** characters. The value is a flag indicating if this character
** is an alphanumeric character or a valid word separator.
** For characters < 255 we maintain a simple array for performance
** reasons. 
** 
** The reason of the hashtable is to cache lookups to Python calls
** like Py_Unicode_ISALNUM()/
*/


#define MISS 0                       // Cache miss

#define IS_TRASH 1                   // not a valid word separator
#define IS_ALNUM 2                   // alphanumeric character
#define IS_SEPARATOR 3               // valid word separator
#define UNSET 255                    // default value

#define HASHTABLESIZE 4096           // size of hashtable


typedef struct
{
    int value;
}
INODE ;


// Create a new node 

INODE * new_inode(int v)
{
    INODE * n;

    n = (INODE *) malloc(sizeof(INODE));
    n->value = v;
    return n;
}

// delete a node 

int del_inode(void * node)
{
    free(node);
    return 1;
}

// compare the values of two nodes

int inode_cmp(void *n1, void *n2)
{
    int v1,v2;

    v1 = ((INODE *) n1)->value;
    v2 = ((INODE *) n2)->value;

    if (v1 < v2)
        return -1;
    else if (v1 > v2)
        return 1;
    else
        return 0;
}

// get the value for a given key

int inode_get(Splitter * self, int v)
{
    INODE * result;
    INODE tmp;

    if (v < 256)
        return self->small_cache[v]==UNSET ? MISS : self->small_cache[v];

    tmp.value = v;
    result = hashtable_search(self->cache, &tmp);

    if (result)
        return  result->value;
    else
        return MISS;
}

// insert a new (key,value) pair 

int inode_set(Splitter * self, int k, int v)
{
    if (k < 256)
        self->small_cache[k] = v;
    else
        hashtable_insert_txng(self->cache, new_inode(k), new_inode(v), 0);

    return 1;
}

// calculate the hash value for a node 

unsigned inode_hash(void *node)
{
    int v;

    v = ((INODE *) node)->value;
    return  v % HASHTABLESIZE;
}

/* 
** Here starts the splitter dance 
*/

static void
Splitter_dealloc(Splitter *self)
{
    hashtable_destroy(self->cache, 1);
    Py_XDECREF(self->list);
    PyMem_DEL(self);
}


/*
** Dummy functions 
*/

static PyObject *
Splitter_concat(Splitter *self, PyObject *other)
{
    PyErr_SetString(PyExc_TypeError, "Cannot concatenate Splitters.");
    return NULL;
}

static PyObject *
Splitter_repeat(Splitter *self, long n)
{
    PyErr_SetString(PyExc_TypeError, "Cannot repeat Splitters.");
    return NULL;
}

static PyObject *
Splitter_slice(Splitter *self, int i, int j)
{
    PyErr_SetString(PyExc_TypeError, "Cannot slice Splitters.");
    return NULL;
}

/*
** __getitem__() support (not used)
*/

static PyObject *
Splitter_item(Splitter *self, int i)
{
    PyObject *item;
    item = PyList_GetItem(self->list, i);
    Py_XINCREF(item);  /* Promote borrowed ref unless exception */
    return item;
}

/*
** Split functions for strings and unicode strings
*/

int splitUnicodeString(Splitter *self,PyObject *doc);
int splitString(Splitter *self,PyObject *doc);

static PyObject *
Splitter_split(Splitter *self, PyObject *args)
{
    PyObject *doc;
    char *encoding = "iso-8859-15";

    Py_XDECREF(self->list);
    self->list = PyList_New(0);
    
    if (! (PyArg_ParseTuple(args,"O|s",&doc, &encoding))) return NULL;

    if (PyString_Check(doc)) {
        if (strlen(encoding) == 0 || !strcmp(encoding,"ascii"))
            splitString(self, doc);
        else {
            PyObject *doc1;
            if (! (doc1 = PyUnicode_FromEncodedObject(doc, encoding, "strict"))) {
                PyErr_SetString(PyExc_UnicodeError,"unicode conversion failed (maybe wrong encoding parameter)");
                return NULL;
            }

            splitUnicodeString(self, doc1);
            Py_XDECREF(doc1);
        } 
    } else if (PyUnicode_Check(doc)) {
        PyObject *doc1; // create a *real* copy since we need to modify the string
        doc1 = PyUnicode_FromUnicode(((PyUnicodeObject *) doc)->str, ((PyUnicodeObject*) doc)->length);
        splitUnicodeString(self, doc1);
        Py_DECREF(doc1);
    } else {
        PyErr_SetString(PyExc_TypeError, "first argument must be  string or unicode");
        return NULL;
    }

    Py_XINCREF(self->list);

    return self->list;
}


/* 
** return a sequence of word positions of a word inside the splitted text
*/

static PyObject *
Splitter_indexes(Splitter *self, PyObject *args)
{
    int i=0, size;
    PyObject *word=NULL,*item=NULL,*r=NULL,*index=NULL;

    if (! (PyArg_ParseTuple(args,"O",&word)))
        return NULL;
    if (! (r=PyList_New(0)))
        return NULL;

    size = PyList_Size(self->list);
    for (i=0;i<size;i++) {
        item=PyList_GET_ITEM(self->list,i);

        if (PyUnicode_Compare(word,item)==0) {
            index=PyInt_FromLong(i);
            if(!index)
                return NULL;
            PyList_Append(r,index);
        }
    }

    return r;
}

/*
** number of splitted words
*/

static int
Splitter_length(Splitter *self)
{
    return PyList_Size(self->list);
}

/*
** class definitions for splitters object
*/

static PySequenceMethods Splitter_as_sequence = {
            (inquiry)Splitter_length,        /*sq_length*/
            (binaryfunc)Splitter_concat,     /*sq_concat*/
            (intargfunc)Splitter_repeat,     /*sq_repeat*/
            (intargfunc)Splitter_item,       /*sq_item*/
            (intintargfunc)Splitter_slice,   /*sq_slice*/
            (intobjargproc)0,                    /*sq_ass_item*/
            (intintobjargproc)0,                 /*sq_ass_slice*/
        };


static struct PyMethodDef Splitter_methods[] =
    {
        { "split", (PyCFunction) Splitter_split, METH_VARARGS,
            "split(doc) -- Split string in one run"
        },
        { "indexes", (PyCFunction)Splitter_indexes, METH_VARARGS,
          "indexes(word) -- Return a list of the indexes of word in the sequence",
        },
        { NULL, NULL }		/* sentinel */
    };


static PyObject *
Splitter_getattr(Splitter *self, char *name)
{
    return Py_FindMethod(Splitter_methods, (PyObject *)self, name);
}

static char SplitterType__doc__[] = "splitter instance for strings or unicode strings";

static PyTypeObject SplitterType = {
                                       PyObject_HEAD_INIT(NULL)
                                       0,                                 /*ob_size*/
                                       "Splitter",                    /*tp_name*/
                                       sizeof(Splitter),              /*tp_basicsize*/
                                       0,                                 /*tp_itemsize*/
                                       /* methods */
                                       (destructor)Splitter_dealloc,  /*tp_dealloc*/
                                       (printfunc)0,                      /*tp_print*/
                                       (getattrfunc)Splitter_getattr, /*tp_getattr*/
                                       (setattrfunc)0,                    /*tp_setattr*/
                                       (cmpfunc)0,                        /*tp_compare*/
                                       (reprfunc)0,                       /*tp_repr*/
                                       0,                                 /*tp_as_number*/
                                       &Splitter_as_sequence,         /*tp_as_sequence*/
                                       0,                                 /*tp_as_mapping*/
                                       (hashfunc)0,                       /*tp_hash*/
                                       (ternaryfunc)0,                    /*tp_call*/
                                       (reprfunc)0,                       /*tp_str*/

                                       /* Space for future expansion */
                                       0L,0L,0L,0L,
                                       SplitterType__doc__ /* Documentation string */
                                   };

/*
** split a non-unicode string
*/

int splitString(Splitter *self,PyObject *doc) 
{
    PyObject *word ;
    char *s,*str;
    int i, inside_word=0, start=0, len;
    register int value, next_value;

    PyString_AsStringAndSize(doc, &str, &len);  
    s = str;

    for (i=0; i<len; i++,s++) {
        char c = *s;

        if (self->casefolding)
            *s = tolower(c);

        value = inode_get(self, c);


        if (value == MISS ) {
            // cache miss

            value = isalnum(c) ? IS_ALNUM : IS_TRASH;
            inode_set(self, c, value);
        }

        if (!inside_word) {
            if (value != IS_TRASH && value != IS_SEPARATOR) {
                start = i;
                inside_word = 1;
            }
        } else {
            
            if (value == IS_SEPARATOR) {
                char next_c = *(s+1);

                next_value = inode_get(self, next_c);

                if (next_value == MISS ) {
                    // cache miss

                    next_value = isalnum(next_c) ? IS_ALNUM : IS_TRASH;
                    inode_set(self, next_c, next_value);
                }
                
                if (next_value == IS_TRASH) { 
                    if (! (i-start<2 && ! self->single_chars)) {
                        word = Py_BuildValue("s#", s-(i-start), min(i-start, self->max_len));
                        PyList_Append(self->list, word);
                        Py_XDECREF(word);
                    }
                    start = i;
                    inside_word = 0;
                }
                
            }
            else if (value == IS_TRASH) {
                if (! (i-start<2 && ! self->single_chars)) {
                    word = Py_BuildValue("s#", s-(i-start), min(i-start, self->max_len));
                    PyList_Append(self->list, word);
                    Py_XDECREF(word);
                }
                start = i;
                inside_word = 0;
            }
        }
    }

    if (inside_word) {
        if (! (i-start<2 && ! self->single_chars)) {
            word = Py_BuildValue("s#", s-(i-start), min(i-start, self->max_len));
            PyList_Append(self->list, word);
            Py_XDECREF(word);
        }
    }

    return 1;
}

/*
** split a unicode string
*/

int splitUnicodeString(Splitter *self,PyObject *doc)
{
    PyObject *word ;
    Py_UNICODE *s;
    int i, inside_word=0, start=0, len;
    register int value, next_value;

    s = ((PyUnicodeObject *) doc)->str;       // start of unicode string
    len = ((PyUnicodeObject *)doc)->length;


    for (i=0; i<len; i++,s++) {
        register Py_UNICODE c;

        c = *s;

        if (self->casefolding)
            *s = Py_UNICODE_TOLOWER(c);

        value = inode_get(self, c);

        if (value == MISS ) {
            // cache miss

            value = Py_UNICODE_ISALNUM(c) ? IS_ALNUM : IS_TRASH;
            inode_set(self, c, value);
        }

        if (!inside_word) {
            if (value != IS_TRASH ) {
                start = i;
                inside_word = 1;
            }
        } else {

            if (value == IS_SEPARATOR) {
                register Py_UNICODE next_c = *(s+1);

                next_value = inode_get(self, next_c);

                if (next_value == MISS ) {
                    // cache miss

                    next_value = Py_UNICODE_ISALNUM(next_c) ? IS_ALNUM : IS_TRASH;
                    inode_set(self, next_c, next_value);
                }
                
                if (next_value == IS_TRASH) { 
                    if (! (i-start<2 && ! self->single_chars)) {
                        word = Py_BuildValue("u#", s-(i-start), min(i-start, self->max_len));
                        PyList_Append(self->list, word);
                        Py_XDECREF(word);
                    }
                    start = i;
                    inside_word = 0;
                }
                
            }

            else if (value==IS_TRASH) {
                if (! (i-start<2 && ! self->single_chars)) {
                    word = Py_BuildValue("u#", s-(i-start), min(i-start, self->max_len));
                    PyList_Append(self->list, word);
                    Py_XDECREF(word);
                }
                start = i;
                inside_word = 0;
            }
        }
    }

    if (inside_word) {
        if (! (i-start<2 && ! self->single_chars)) {
            word = Py_BuildValue("u#", s-(i-start), min(i-start, self->max_len));
            PyList_Append(self->list, word);
            Py_XDECREF(word);
        }
    }

    return 1;
}


/* 
** constructor stuff
*/

static char *splitter_args[] = {"separator","singlechar","maxlen","casefolding",NULL};


static PyObject *
newSplitter(PyObject *modinfo, PyObject *args,PyObject *keywds)
{
    int i, max_len=64, single_char=0, casefolding=1;
    Splitter *self=NULL;
    unsigned char *separator = "";

    if (! (PyArg_ParseTupleAndKeywords(
                    args,
                    keywds,
                    "|siii",
                    splitter_args,
                    &separator,
                    &single_char,
                    &max_len,
                    &casefolding))) return NULL;

    if (casefolding<0 || casefolding>1) {
        PyErr_SetString(PyExc_ValueError,"casefolding must be 0 or 1");
        return NULL;
    }

    if (single_char<0 || single_char>1) {
        PyErr_SetString(PyExc_ValueError,"singlechar must be 0 or 1");
        return NULL;
    }

    if (max_len<1 || max_len>128) {
        PyErr_SetString(PyExc_ValueError,"maxlen must be between 1 and 128");
        return NULL;
    }

    if (! (self = PyObject_NEW(Splitter, &SplitterType)))
        return NULL;

    self->max_len            = max_len;
    self->single_chars       = single_char;
    self->casefolding        = casefolding;
    self->list               = PyList_New(0);
    self->cache              = hashtable_new_txng(
                               (dict_cmp_func) inode_cmp,
                               (dict_hsh_func) inode_hash,
                               (dict_del_func) del_inode,
                               NULL,
                               HASHTABLESIZE);

    // assign small cache
    for (i=0;i<256;i++)
        self->small_cache[i] = UNSET ;

    // assign separator characters to small cache
    for (i=0; i<strlen(separator); i++)  
        self->small_cache[(int) separator[i]] =  IS_SEPARATOR;


    return (PyObject*) self;
}

static struct PyMethodDef Splitter_module_methods[] =
    {
        { "TXNGSplitter", (PyCFunction)newSplitter, METH_VARARGS|METH_KEYWORDS,
            "TXNGSplitter([,maxlen][,singlechar][,casefolding][,separator]) "
            "-- Return a word splitter"
        },
        { NULL, NULL }
    };

static char Splitter_module_documentation[] =
    "Split a string or a unicode string into a sequence of unicode strings"
    ;


void
initTXNGSplitter(void)
{
    Py_InitModule3("TXNGSplitter", Splitter_module_methods,
                       Splitter_module_documentation);
}
