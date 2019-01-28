""" Ported Unindex._apply_index from
    Products.ZCatalog-2.13.27/Products/PluginIndexes/common/UnIndex.py
    because it's a lot faster.
"""
import logging
from cgi import escape

from BTrees.IIBTree import intersection
from BTrees.IIBTree import IISet
from BTrees.IIBTree import multiunion

from Products.PluginIndexes.common.util import parseIndexRequest

from Products.PluginIndexes.common.UnIndex import UnIndex


log = logging.getLogger(__name__)


def patch_zcatalog_unindex():
    old_apply_index = UnIndex._apply_index
    UnIndex._apply_index = _apply_index
    log.info('Applied UnIndex._apply_index patch!')


def _apply_index(self, request, resultset=None):
    """Apply the index to query parameters given in the request arg.

    The request argument should be a mapping object.

    If the request does not have a key which matches the "id" of
    the index instance, then None is returned.

    If the request *does* have a key which matches the "id" of
    the index instance, one of a few things can happen:

      - if the value is a blank string, None is returned (in
	order to support requests from web forms where
	you can't tell a blank string from empty).

      - if the value is a nonblank string, turn the value into
	a single-element sequence, and proceed.

      - if the value is a sequence, return a union search.

      - If the value is a dict and contains a key of the form
	'<index>_operator' this overrides the default method
	('or') to combine search results. Valid values are "or"
	and "and".

    If None is not returned as a result of the abovementioned
    constraints, two objects are returned.  The first object is a
    ResultSet containing the record numbers of the matching
    records.  The second object is a tuple containing the names of
    all data fields used.

    FAQ answer:  to search a Field Index for documents that
    have a blank string as their value, wrap the request value
    up in a tuple ala: request = {'id':('',)}
    """
    record = parseIndexRequest(request, self.id, self.query_options)
    if record.keys is None:
	return None

    index = self._index
    r     = None
    opr   = None

    # experimental code for specifing the operator
    operator = record.get('operator',self.useOperator)
    if not operator in self.operators :
	raise RuntimeError("operator not valid: %s" % escape(operator))

    # Range parameter
    range_parm = record.get('range',None)
    if range_parm:
	opr = "range"
	opr_args = []
	if range_parm.find("min")>-1:
	    opr_args.append("min")
	if range_parm.find("max")>-1:
	    opr_args.append("max")

    if record.get('usage',None):
	# see if any usage params are sent to field
	opr = record.usage.lower().split(':')
	opr, opr_args=opr[0], opr[1:]

    if opr=="range":   # range search
	if 'min' in opr_args: lo = min(record.keys)
	else: lo = None
	if 'max' in opr_args: hi = max(record.keys)
	else: hi = None
	if hi:
	    setlist = index.values(lo,hi)
	else:
	    setlist = index.values(lo)

	# If we only use one key, intersect and return immediately
	if len(setlist) == 1:
	    result = setlist[0]
	    if isinstance(result, int):
		result = IISet((result,))
	    return result, (self.id,)

	if operator == 'or':
	    tmp = []
	    for s in setlist:
		if isinstance(s, int):
		    s = IISet((s,))
		tmp.append(s)
	    r = multiunion(tmp)
	else:
	    # For intersection, sort with smallest data set first
	    tmp = []
	    for s in setlist:
		if isinstance(s, int):
		    s = IISet((s,))
		tmp.append(s)
	    if len(tmp) > 2:
		setlist = sorted(tmp, key=len)
	    else:
		setlist = tmp
	    r = resultset
	    for s in setlist:
		# the result is bound by the resultset
		r = intersection(r, s)

    else: # not a range search
	# Filter duplicates
	setlist = []
	for k in record.keys:
	    s = index.get(k, None)
	    # If None, try to bail early
	    if s is None:
		if operator == 'or':
		    # If union, we can't possibly get a bigger result
		    continue
		# If intersection, we can't possibly get a smaller result
		return IISet(), (self.id,)
	    elif isinstance(s, int):
		s = IISet((s,))
	    setlist.append(s)

	# If we only use one key return immediately
	if len(setlist) == 1:
	    result = setlist[0]
	    if isinstance(result, int):
		result = IISet((result,))
	    return result, (self.id,)

	if operator == 'or':
	    # If we already get a small result set passed in, intersecting
	    # the various indexes with it and doing the union later is
	    # faster than creating a multiunion first.
	    if resultset is not None and len(resultset) < 200:
		smalllist = []
		for s in setlist:
		    smalllist.append(intersection(resultset, s))
		r = multiunion(smalllist)
	    else:
		r = multiunion(setlist)
	else:
	    # For intersection, sort with smallest data set first
	    if len(setlist) > 2:
		setlist = sorted(setlist, key=len)
	    r = resultset
	    for s in setlist:
		r = intersection(r, s)

    if isinstance(r, int):
	r = IISet((r, ))
    if r is None:
	return IISet(), (self.id,)
    else:
	return r, (self.id,)

