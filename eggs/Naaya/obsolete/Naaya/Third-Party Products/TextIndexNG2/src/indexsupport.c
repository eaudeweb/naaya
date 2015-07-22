/*

 TextIndexNG                The next generation TextIndex for Zope

 This software is governed by a license. See
 LICENSE.txt for the terms of this license.

*/


#include "Python.h"
#include <stdlib.h>

PyObject *IIBTreeModule, *IISet, *IIBucket;


int importIIBTreeModule(void)
{
    PyObject  *mod_dict;

    IIBTreeModule = PyImport_ImportModule("BTrees.IIBTree");
    if (! IIBTreeModule)
        return 0;

    mod_dict = PyModule_GetDict(IIBTreeModule);

    IISet = PyDict_GetItemString(mod_dict, "IISet");
    if (! IISet)
        return 0;

    IIBucket = PyDict_GetItemString(mod_dict, "IIBucket");
    if (! IIBucket)
        return 0;

    return 1;
}

PyObject *IISetFactory(void)
{
    PyObject *iiset;
    iiset = PyObject_CallFunction(IISet,NULL);
    return iiset;
}

PyObject *IIBucketFactory(void)
{
    PyObject *iibucket;
    iibucket = PyObject_CallFunction(IIBucket,NULL);
    return iibucket;
}



static PyObject *
stopwordfilter(PyObject *modinfo, PyObject *args)
{
    PyObject *stopwords, *words, *list;
    int i, len;

    list = PyList_New(0);

    if (! (PyArg_ParseTuple(args,"OO",&words,&stopwords)))
        return NULL;

    words = PySequence_Fast(words, "1st argument must be a sequence");
    len = PyObject_Length(words);

    for (i=0; i<len; i++) {
        PyObject *item  = PySequence_Fast_GET_ITEM(words, i);

        if (PyDict_GetItem(stopwords, item) == NULL)
            PyList_Append(list,item);
    }

    Py_XDECREF(words);

    return list;
}


static PyObject *
listIndexes(PyObject *modinfo, PyObject *args)
{
    PyObject *wordlist, *word,*list;
    int i;

    list = PyList_New(0);

    if (! (PyArg_ParseTuple(args,"OO",&wordlist,&word)))
        return NULL;

    for (i=0; i<PyList_Size(wordlist); i++) {
        PyObject *item;

        item = PyList_GetItem(wordlist,i);

        if (! PyObject_Compare(item, word))
            PyList_Append(list,PyInt_FromLong(i));
    }

    return list;
}

/*
    Arguments:
 
    - fwdIdx  --  forward index (OIBTree)
    - reverseIdx -- reverse index (IOBtree)
    - wordIds -- sequence of wordIds to be inserted 
    - docId --  documentId
*/

PyObject *storageBatchInsert(PyObject *modinfo,PyObject *args)
{

    PyObject *fwdIdx,*revIdx, *wids, *wid, *docId, *insert, *update,*iiset;
    int i, len;

    if (! PyArg_ParseTuple(args, "OOOO", &fwdIdx,&revIdx,&wids,&docId))
        return NULL;

    if (! PyMapping_Check(fwdIdx)) {
        PyErr_SetString(PyExc_TypeError, "1st argument must be IOBTree instance");
        return NULL;
    }

    if (! PyMapping_Check(revIdx)) {
        PyErr_SetString(PyExc_TypeError, "2nd argument must be IOTree instance");
        return NULL;
    }

    if (! PySequence_Check(wids)) {
        PyErr_SetString(PyExc_TypeError, "3rd argument must be sequence");
        return NULL;
    }

    if (! PyInt_Check(docId)) {
        PyErr_SetString(PyExc_TypeError, "4th argument must be integer");
        return NULL;
    }


    // Forward index

    len = PyObject_Length(wids);
    wids = PySequence_Fast(wids, "3rd argument must be a sequence");


    for (i=0; i<len;i++) {
        PyObject *docIds;

        wid = PySequence_Fast_GET_ITEM(wids,i);

        if (! PyMapping_HasKey(fwdIdx,wid)) {
            PyObject *iiset;
            iiset = IISetFactory();
            PyObject_SetItem(fwdIdx, wid, iiset);
        }

        docIds = PyObject_GetItem(fwdIdx, wid);
        insert = PyObject_GetAttrString(docIds, "insert");
        PyObject_CallFunction(insert,"O", docId);
    }

    // Reverse index

    if (PyMapping_HasKey(revIdx, docId)) {
        iiset = PyObject_GetItem(revIdx, docId);
    } else {
        iiset = IISetFactory();
    }

    update = PyObject_GetAttrString(iiset, "update");
    PyObject_CallFunction(update,"O", wids);
    PyObject_SetItem(revIdx, docId, iiset);

    return Py_None;
}


/*
    Arguments:
 
    - fwdIdx  --  forward index (OIBTree)
    - reverseIdx -- reverse index (IOBtree)
    - words -- sequence of words to be inserted 
*/

PyObject *vocabularyBatchInsert(PyObject *modinfo,PyObject *args)
{

    PyObject *fwdIdx,*revIdx, *lst, *word, *wid;
    PyObject *wids;
    int i;

    if (! PyArg_ParseTuple(args, "OOO", &fwdIdx,&revIdx,&lst))
        return NULL;

    if (! PyMapping_Check(fwdIdx)) {
        PyErr_SetString(PyExc_TypeError, "1st argument must be OIBTree instance");
        \
        return NULL;
    }

    if (! PyMapping_Check(revIdx)) {
        PyErr_SetString(PyExc_TypeError, "2nd argument must be IOTree instance");
        \
        return NULL;
    }

    if (! PySequence_Check(lst)) {
        PyErr_SetString(PyExc_TypeError, "3rd argument must be sequence");
        return NULL;
    }

    wids = PyList_New(0);

    for (i=0; i<PySequence_Length(lst);i++) {
        word = PySequence_GetItem(lst,i);

        if (PyMapping_HasKey(fwdIdx,word)) {
            wid = PyObject_GetItem(fwdIdx,word);
        } else {

            do {
                wid = PyInt_FromLong( rand() );
            } while(PyMapping_HasKey(revIdx, wid));

            PyObject_SetItem(fwdIdx, word, wid);
            PyObject_SetItem(revIdx, wid,  word);
        }

        PyList_Append(wids, wid);

        Py_XDECREF(word);
        Py_XDECREF(wid);
    }

    return wids;
}


PyObject *fastrandom(PyObject *modinfo,PyObject *args)
{
    PyObject *rnd;
    rnd = PyInt_FromLong(rand());
    return rnd;
}
    


static struct PyMethodDef indexsupport_module_methods[] =
    {
        { "fastrandom", (PyCFunction) fastrandom, METH_VARARGS,
            "fastrandom() " "-- fast random number generator"
        },
        { "stopwordfilter", (PyCFunction) stopwordfilter, METH_VARARGS,
            "stopwordfilter(wordslist,stopword dict') " "-- filters words from wordslist that are stopwords"
        },
        { "vocabBatchInsert", (PyCFunction) vocabularyBatchInsert, METH_VARARGS,
          "vocabBatchInsert(fwdIdx,revIdx,wordLst)" "-- inserts forward and backward entries for vocabularies"
        },
        { "storageBatchInsert", (PyCFunction) storageBatchInsert, METH_VARARGS,
          "storageBatchInsert(fwdIdx,revIdx,wordLst,docId)" "-- inserts forward and backward entries for WordDocStorage"
        },
        { "listIndexes", (PyCFunction) listIndexes, METH_VARARGS,
          "listIndexes(list of words',word) " "-- find all positions of word in a list of words"
        },
        { NULL, NULL }
    };


void
initindexsupport(void)
{
    PyObject *m, *d;
    char *rev="$Revision: 1.9 $";

    /* Create the module and add the functions */
    m = Py_InitModule3("indexsupport", indexsupport_module_methods,
                        "TextIndexNG support module"); 

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "__version__",
                         PyString_FromStringAndSize(rev+11,strlen(rev+11)-2));
    if (! importIIBTreeModule()) {
        Py_FatalError("importing IIBTree failed");
    }
    if (PyErr_Occurred())
        Py_FatalError("can't initialize module indexsupport");
}

