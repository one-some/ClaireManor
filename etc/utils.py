def get_subclasses(base_class: type) -> list[type]:
    out = set()
    new = [base_class]

    while new:
        cls = new.pop()
        if cls != base_class:
            out.add(cls)
        
        for sub in cls.__subclasses__():
            if sub in out: continue
            new.append(sub)
    return out
