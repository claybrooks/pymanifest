import argparse
import os
import fnmatch
import logging


class ArgSet:
    def __init__(self, files, directories, recurse_directories, manifests, patterns):
        self.files = files
        self.directories = directories
        self.recurse_directories = recurse_directories
        self.manifests = manifests
        self.patterns = patterns


DEFAULT_ARG_MAP = {
    '--file'                        : '--file',
    '--directory'                   : '--directory',
    '--recurse-directory'           : '--recurse-directory',
    '--manifest'                    : '--manifest',
    '--exclude-file'                : '--exclude-file',
    '--exclude-directory'           : '--exclude-directory',
    '--exclude-recurse-directory'   : '--exclude-recurse-directory',
    '--exclude-manifest'            : '--exclude-manifest',
    '--pattern'                     : '--pattern',
    '--exclude-pattern'             : '--exclude-pattern',
}

def __mimic_ap_rename(arg:str):
    if arg.startswith('--'):
        arg = arg[2:]
    arg = arg.replace('-', '_')
    return arg

def add_args(ap: argparse.ArgumentParser, arg_map:dict[str, dict[str,str]]=None):

    if arg_map is None:
        arg_map = dict(DEFAULT_ARG_MAP)

    ap.add_argument(
        arg_map['--file'],
        action='append',
        default=[],
        help='Full path to a file to include.'
    )

    ap.add_argument(
        arg_map['--directory'],
        action='append',
        default=[],
        help='Full path to a directory of files to include.'
    )

    ap.add_argument(
        arg_map['--recurse-directory'],
        action='append',
        default=[],
        help='Full path to a directory of files and subdirectories to include.'
    )

    ap.add_argument(
        arg_map['--manifest'],
        action='append',
        default=[],
        help='Full path to a file that contains newline delimited paths to files and directories to include.'
    )

    ap.add_argument(
        arg_map['--exclude-file'],
        action='append',
        default=[],
        help='Full path to file to exclude.'
    )

    ap.add_argument(
        arg_map['--exclude-directory'],
        action='append',
        default=[],
        help='Full path to a directory to exclude.'
    )

    ap.add_argument(
        arg_map['--exclude-recurse-directory'],
        action='append',
        default=[],
        help='Full path to a directory to exclude.'
    )

    ap.add_argument(
        arg_map['--exclude-manifest'],
        action='append',
        default=[],
        help='Full path to a file that contains newline delimited paths to files and directories to exclude.'
    )

    ap.add_argument(
        arg_map['--pattern'],
        action='append',
        default=[],
        help='Patterns of files to include.'
    )

    ap.add_argument(
        arg_map['--exclude-pattern'],
        action='append',
        default=[],
        help='Pattern of files to exclude.'
    )


def __process_file(path:str, out:set[str], err:set[str]):
    out.add(path) if os.path.isfile(path) else err.append(path)


def __process_directory(path:str, out:set[str], err:set[str]):
    path = os.path.realpath(path)
    out.update([os.path.join(path, x) for x in next(os.walk(path))[2]]) if os.path.isdir(path) else err.append(path)


def __process_recurse_directory(path:str, out:set[str], err:set[str]):
    path = os.path.realpath(path)

    if not os.path.isdir(path):
        err.append(path)
    else:
        for dirpath, dirnames, filenames in os.walk(path):
            out.update([os.path.join(dirpath, x) for x in filenames])


def __process_manifest(path:str, out:set[str], err:set[str]):

    if not os.path.isfile(path):
        return

    with open(path, 'r') as f:
        for line in f:
            if os.path.isfile(line):
                __process_file(line, out, err)
            elif os.path.isdir(line):
                __process_directory(line, out, err)
            else:
                err.add(line)


def __process_patterns(fromList:list[str], filters:list[str]):
    matched = []
    for filt in filters:
        matched.extend(fnmatch.filter(fromList, filt))
    return set(matched)


def __process_items(items:set[str], include:set[str], missing:set[str], processor):
    for item in items:
        processor(item, include, missing)


def __process_arg_set(arg_set:ArgSet):
    files = set()
    err_files = set()
    err_directories = set()

    __process_items(arg_set.files,              files, err_files,       __process_file)
    __process_items(arg_set.directories,        files, err_directories, __process_directory)
    __process_items(arg_set.recurse_directories,files, err_directories, __process_recurse_directory)
    __process_items(arg_set.manifests,          files, err_files,       __process_manifest)

    return files, err_files, err_directories


def process_from_args(args, arg_map:dict[str, str]=None, fail_on_missing:bool=False):

    if arg_map is None:
        arg_map = dict(DEFAULT_ARG_MAP)

    attr_map = {}
    for k,v in arg_map.items():
        attr_map[k] = __mimic_ap_rename(v)

    include = ArgSet(
        getattr(args, attr_map['--file']),
        getattr(args, attr_map['--directory']),
        getattr(args, attr_map['--recurse-directory']),
        getattr(args, attr_map['--manifest']),
        getattr(args, attr_map['--pattern'])
    )

    exclude = ArgSet(
        getattr(args, attr_map['--exclude-file']),
        getattr(args, attr_map['--exclude-directory']),
        getattr(args, attr_map['--exclude-recurse-directory']),
        getattr(args, attr_map['--exclude-manifest']),
        getattr(args, attr_map['--exclude-pattern'])
    )

    return process(include, exclude, fail_on_missing)


def process(include, exclude, fail_on_missing:bool=False):

    include_files, err_include_files, err_include_directories = __process_arg_set(include)
    exclude_files, err_exclude_files, err_exclude_directories = __process_arg_set(exclude)

    # get the first difference between what is to be included and excluded
    curr_matched = include_files - exclude_files

    # only run pattern matching if something was provided
    if len(include.patterns) > 0:
        include = __process_patterns(curr_matched, set(include.patterns))
        curr_matched = curr_matched.intersection(include)

    # only run pattern matching if something was provided
    if len(exclude.patterns) > 0:
        exclude = __process_patterns(curr_matched, set(exclude.patterns))
        curr_matched = curr_matched - exclude

    return list(curr_matched)
