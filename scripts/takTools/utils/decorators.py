import time
from functools import wraps
from maya import cmds


def undoAtOnce(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        result = func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
        return result
    return wrapper


def printElapsedTime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        print('"{}()" takes time to run {}s.'.format(func.__name__, round(elapsedTime, 2)))
        return result
    return wrapper
