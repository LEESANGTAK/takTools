class Event:
    def __init__(self, *argTypes):
        self._listeners = []
        self._argTypes = argTypes

    def AddListener(self, callback):
        if callable(callback) and callback not in self._listeners:
            self._listeners.append(callback)

    def RemoveListener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def Invoke(self, *args, **kwargs):
        if self._argTypes:
            if len(args) != len(self._argTypes):
                raise TypeError(f"Expected {len(self._argTypes)} arguments, got {len(args)}.")
            for i, (arg, expected_type) in enumerate(zip(args, self._argTypes)):
                if not isinstance(arg, expected_type):
                    raise TypeError(f"Argument {i} must be {expected_type.__name__}, got {type(arg).__name__}.")

        for callback in self._listeners:
            callback(*args, **kwargs)

    def ClearListeners(self):
        self._listeners.clear()
