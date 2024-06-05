
#& Singleton Instance Container
def Singleton(clazz):
    instances = {}
    def get_instance(*args, **kwargs):
        if clazz not in instances:
            instances[clazz] = clazz(*args, **kwargs)
        return instances[clazz]
    return get_instance
