# reliable-finalizer
`reliable-finalizer` is a small utility library for convenient implementation
of finalizers in python
## Installation
```
pip install reliable-finalizer
```
## Usage

```python
from reliable_finalizer import reliable_finalizer

class UsefulClass:
    ...  # This is a class that requires some cleanup on instance destruction
    
    # This method will be called on object before it is garbage collected OR at the end of the program
    @reliable_finalizer
    def destruct(self): 
        ...  # The cleanup code       
```

## Why use `reliable-finalizer`?
This library's purpose is to provide convenient syntax for reliable finalization in Python.
The built-in solution for finalization, [\_\_del\_\_()](https://docs.python.org/3/reference/datamodel.html#object.__del__), does not make guarantees strong enough to be adequately used
with an arbitrary interpreter (although it is somewhat consistent in [CPython](https://docs.python.org/3/glossary.html#term-CPython)).
Namely, it can be called multiple times, and is not guaranteed to be called at all! - `__del__()` is not a great place for cleanup code.

Standard library offers a more robust solution: [weakref.finalize()](https://docs.python.org/3/library/weakref.html#finalizer-objects). It does basically the same thing `__del__()` does, but gives stronger guarantees about its behavior: the callback is invoked once and only once.

`reliable_finalizer` decorator is a utility for creating such finalizers. Any instance of a class with `reliable_finalizer`-decorated method will have a finalizer assigned to it.
Because of that, using `reliable_finalizer` is syntactically similar to using `__del__()` - all one needs is to create a method.

## Additional details and limitations
### Manual finalizer invocation 
Calling a method decorated with `reliable_finalizer` on an instance invokes the underlying finalizer, so calling it manually is completely fine - it will still only be called once. This can be useful, for example, if you want to additionally implement [context manager protocol](https://docs.python.org/3/reference/datamodel.html#context-managers) in your class:
```python
from reliable_finalizer import reliable_finalizer

class UsefulClass:
    ...  # This is a class that requires some cleanup on instance destruction
    
    # This method will be called on object before it is garbage collected OR at the end of the program
    @reliable_finalizer
    def destruct(self): 
        ...  # The cleanup code 
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destruct()
```
### Using finalizers with slots
When using `reliable_finalizer`, the underlying weakref finalizer of an instance is saved to its `__finalizer__` attribute.
If your class does not have a `__dict__` slot, it must have `__finalizer__` slot in order to use `reliable_finalizer`:
```python
from reliable_finalizer import reliable_finalizer

class UsefulClass:
    ...  # This is a class that requires some cleanup on instance destruction
    
    __slots__ = [
        ...,  # Slots for the class
        '__finalizer__'  # This slot is required for reliable_finalizer to work, if "__dict__" is not a slot 
    ]
    
    # This method will be called on object before it is garbage collected OR at the end of the program
    @reliable_finalizer
    def destruct(self): 
        ...  # The cleanup code       
```