import doctest
import importlib
import pkgutil


def run_package_doctests(pkg_name: str, verbose=False):
    mod_names = [name for _, name, _ in pkgutil.iter_modules([pkg_name])]

    for mod_name in mod_names:
        doctest.testmod(importlib.import_module(f'{pkg_name}.{mod_name}'), verbose=verbose)


if __name__ == '__main__':
    run_package_doctests('util')
    run_package_doctests('trader')
