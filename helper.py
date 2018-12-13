import os, errno


def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def escape_url(text):
    return text.replace('://', '-').replace(':', '-').replace('/', '-')
