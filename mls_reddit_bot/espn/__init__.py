import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = module
