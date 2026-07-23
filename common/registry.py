class Registry:
    """A reusable name -to-object registry."""
    
    def __init__(self, name):
        self.name = name
        self._registry = {}
        
    def register(self, key):
        def decorator(obj):
            if key in self._registry:
                raise KeyError(
                    f"{key!r} already registered in {self.name!r}"
                )
            self._registry[key] = obj
            return obj
        return decorator
    
    def get(self, key):
        if key not in self._registry:
            raise KeyError(
                f"{key!r} not found in {self.name !r}."
                f"Available : {list(self._registry)}"
            )
        return self._registry[key]
    
    def __contains__(self, item):
        return item in self._registry
    
    def keys(self):
        return self._registry.keys()