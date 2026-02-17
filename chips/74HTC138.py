from libs.ele import Group as EGroup

class _74HTC128():
    def __init__(self):
        self._in = EGroup(3)
        self._out = EGroup(8)
        
    def update(self):
        pins = self._in.state
        
        if pins == [False, False, False]:
            self._out.signal([True, False, False, False, False, False, False, False])
        elif pins == [True, False, False]:
            self._out.signal([False, True, False, False, False, False, False, False])
        elif pins == [False, True, False]:
            self._out.signal([False, False, True, False, False, False, False, False])
        elif pins == [True, True, False]:
            self._out.signal([False, False, False, True, False, False, False, False])
        elif pins == [False, False, True]:
            self._out.signal([False, False, False, False, True, False, False, False])
        elif pins == [True, False, True]:
            self._out.signal([False, False, False, False, False, True, False, False])
        elif pins == [False, True, True]:
            self._out.signal([False, False, False, False, False, False, True, False])
        elif pins == [True, True, True]:
            self._out.signal([False, False, False, False, False, False, False, True])
