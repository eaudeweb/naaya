__cvs_id__= "$Id: $"

class Directional(object):
    def set_direction(self, direction):
        self._direction_forced = direction
        
    def set_direction_inherited(self, direction):
        self._direction_inherited = direction

    def get_direction(self):
        if hasattr(self, '_direction_forced'):
            return self._direction_forced
        return self._direction_inherited
