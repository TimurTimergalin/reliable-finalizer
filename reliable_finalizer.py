from functools import wraps
from weakref import finalize


class MultipleFinalizersException(Exception):
    """Raised when trying to initialize class with multiple reliable finalizers."""


class ReliableFinalizer:
    """
    Marks method as a finalizer. It is guaranteed to be called once and only once, when object is garbage collected
    OR at the end of the program. Reliable finalizers may also be called manually.

    Trying to create class with multiple reliable finalizers will raise `MultipleFinalizersException`.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        return getattr(owner, self.finalizer_name).__get__(instance)

    def __set_name__(self, owner, name):
        if hasattr(owner, "__has_reliable_finalizer__") and owner.__has_reliable_finalizer__:
            raise MultipleFinalizersException(f"Class {owner.__name__} already has a reliable finalizer")

        owner.__has_reliable_finalizer__ = True

        old_init = owner.__init__

        @wraps(old_init)
        def new_init(obj, *args, **kwargs):
            nonlocal old_init
            old_init(obj, *args, **kwargs)
            obj.__finalizer__ = finalize(obj, self.method, obj)

        @wraps(self.method)
        def new_finalizer(obj):
            return obj.__finalizer__()

        owner.__init__ = new_init
        setattr(owner, name, new_finalizer)
        self.finalizer_name = name


reliable_finalizer = ReliableFinalizer


__all__ = [
    "reliable_finalizer"
]
