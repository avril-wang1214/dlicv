import importlib


def get_library_version(lib):
    """Try to get the version of a library if it has been installed.

    Args:
        lib (str): The name of library.

    Returns:
        None | str: If the library has been installed, return version.
    """
    try:
        lib = importlib.import_module(lib)
        if hasattr(lib, '__version__'):
            version = lib.__version__
        else:
            version = None
    except Exception:
        version = None

    return version


def get_backend_version():
    """Get the version dictionary of some supported backend.

    Returns:
        Dict: The name and the version of some supported backend.
    """
    backend_library_list = ['tensorrt', 'onnxruntime']
    version_dict = dict()
    for backend in backend_library_list:
        version_dict[backend] = get_library_version(backend)
    return version_dict