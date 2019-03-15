#!/usr/bin/env python3

import os
import errno


def mkdir_p(path):
    """See https://stackoverflow.com/a/600612.
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def windows_filename_filter(name):
    # Replace ':*?"<>/\|' to chinese characters if possible.
    name = name.replace(':', '：').replace('?', '？').replace('"', '“')
    name = name.replace('<', '《').replace('>', '》').replace('*', '※')
    name = name.replace('/', '-').replace('\\', '-')
    return name