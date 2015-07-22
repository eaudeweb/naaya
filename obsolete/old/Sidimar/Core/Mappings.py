# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania
# Cornel Nitu, Finsiel Romania
#
#$Id: Mappings.py 3445 2005-04-22 19:16:30Z nituacor $

__version__='$Revision: 1.10 $'[11:-2]


class Mappings:
    """ """

    def __init__(self):
        pass

    def _convert(self, s):
        """ convert strings from None to empty """
        if s is None:   return ''
        else:   return s

    #------------- themes -------------------#
    def mp_supplier(self, rec):
        return self._convert(rec.get('supplier', ''))

    def mp_description(self, rec):
        return self._convert(rec.get('description', ''))

    def mp_region(self, rec):
        return self._convert(rec.get('descr', ''))

    def mp_codreg(self, rec):
        return self._convert(rec.get('idfornit', ''))

    def mp_codmonit(self, rec):
        return self._convert(rec.get('codmonit', ''))

    def mp_descrmonit(self, rec):
        return self._convert(rec.get('descr', ''))

    def mp_year(self, rec):
        return self._convert(rec.get('anno_campag', ''))

    def mp_codparam(self, rec):
        """ """
        return self._convert(rec.get('codparam', ''))

    def mp_unita(self, rec):
        """ """
        return self._convert(rec.get('unita', ''))

    def mp_nome(self, rec):
        """ """
        return self._convert(rec.get('nome', ''))

    def mp_limite_ril(self, rec):
        """ """
        return self._convert(rec.get('limite_ril', ''))

    def mp_paramdescr(self, rec):
        """ """
        return self._convert(rec.get('paramdescr', ''))

    def mp_staz(self, rec):
        """ """
        return self._convert(rec.get('staz', ''))

    def mp_latg(self, rec):
        """ """
        return self._convert(rec.get('latg', ''))

    def mp_latp(self, rec):
        """ """
        return self._convert(rec.get('latp', ''))

    def mp_lats(self, rec):
        """ """
        return self._convert(rec.get('lats', ''))

    def mp_latpc(self, rec):
        """ """
        return self._convert(rec.get('latpc', ''))

    def mp_longg(self, rec):
        """ """
        return self._convert(rec.get('longg', ''))

    def mp_longp(self, rec):
        """ """
        return self._convert(rec.get('longp', ''))

    def mp_longs(self, rec):
        """ """
        return self._convert(rec.get('longs', ''))

    def mp_longpc(self, rec):
        """ """
        return self._convert(rec.get('longpc', ''))

    def mp_codistat(self, rec):
        """ """
        return self._convert(rec.get('codistat', ''))

    def mp_tipo_staz(self, rec):
        """ """
        return self._convert(rec.get('tipo_staz', ''))

    def mp_prof_tot(self, rec):
        """ """
        return self._convert(rec.get('prof_tot', ''))

    def mp_campag(self, rec):
        """ """
        return self._convert(rec.get('campag', ''))

    def mp_dist_riva(self, rec):
        """ """
        return self._convert(rec.get('dist_riva', ''))

    def mp_distsup(self, rec):
        """ """
        return self._convert(rec.get('distsup', ''))

    def mp_progrprel(self, rec):
        """ """
        return self._convert(rec.get('progrprel', ''))

    def mp_valore(self, rec):
        """ """
        return self._convert(rec.get('valore', ''))

    def mp_fornit(self, rec):
        """ """
        return self._convert(rec.get('fornit', ''))

    def mp_monit(self, rec):
        """ """
        return self._convert(rec.get('monit', ''))

    def mp_data(self, rec):
        return self._convert(rec.get('data', ''))

    def mp_distanza(self, rec):
        return self._convert(rec.get('distanza', ''))

    def mp_indice(self, rec):
        return self._convert(rec.get('indice', ''))

    def mp_nomespecie(self, rec):
        return self._convert(rec.get('nome_specie', ''))

    def mp_minvalue(self, rec):
        return self._convert(rec.get('min(valore)', ''))

    def mp_maxvalue(self, rec):
        return self._convert(rec.get('max(valore)', ''))