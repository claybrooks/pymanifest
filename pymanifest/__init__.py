import argparse
import os


def add_args(ap: argparse.ArgumentParser, arg_map:dict[str, dict[str,str]]=None):

    ap.add_argument(
        '--file',
        action='append',
        default=[],
        help='Full path to a file to parse'
    )

    ap.add_argument(
        '--directory',
        action='append',
        default=[],
        help='Full path to a directory of files to parse'
    )

    ap.add_argument(
        '--manifest',
        action='append',
        default=[],
        help='Full path to a file that contains newline delimited files and directories to parse'
    )

    ap.add_argument(
        '--ignore-file',
        action='append',
        default=[],
        help='Full path to file to ignore'
    )

    ap.add_argument(
        '--ignore-directory',
        action='append',
        default=[],
        help='Full path to a directory to ignore'
    )

    ap.add_argument(
        '--ignore-manifest',
        action='append',
        default=[],
        help='Full path to a file that contains newline delimited files and directories to ignore'
    )


def __process_file(path:str, out_list:list[str], missing_list:list[str]):
    out_list.append(path) if os.path.isfile(path) else missing_list.append(path)


def __process_directory(path:str, out_list:list[str], missing_list:list[str]):
    out_list.extend(next(os.walk(path))[2]) if os.path.isdir(path) else missing_list.append(path)


def __process_manifest(path:str, out_list:list[str], missing_list:list[str]):

    if not os.path.isfile(path):
        return

    with open(path, 'r') as f:
        for line in f:
            if os.path.isfile(line):
                __process_file(line, out_list, missing_list)
            elif os.path.isdir(line):
                __process_directory(line, out_list, missing_list)


def process_from_args(args, arg_map:dict[str, str]=None, fail_on_missing:bool=False):

    return process(
        args.file,
        args.ignore_file,
        args.directory,
        args.ignore_directory,
        args.manifest,
        args.ignore_manifest
    )


def process(files, ignore_files, directories, ignore_directories, manifests, ignore_manifests, fail_on_missing:bool=False):
    missing_include_files = []
    missing_exclude_files = []

    missing_include_directories = []
    missing_exclude_directories = []

    files_to_include = []
    files_to_exclude = []

    for file in files:
        __process_file(file, files_to_include, missing_include_files)

    for file in ignore_files:
        __process_file(file, files_to_exclude, missing_exclude_files)

    for directory in directories:
        __process_directory(directory, files_to_include, missing_include_directories)

    for directory in ignore_directories:
        __process_directory(directory, files_to_exclude, missing_exclude_directories)

    for manifest in manifests:
        __process_manifest(args.manifest, files_to_include, missing_include_files)

    for manifest in ignore_manifests:
        __process_manifest(args.ignore_manifest, files_to_exclude, missing_exclude_files)

    missing_include_files_set = set(missing_include_files)
    missing_exclude_files_set = set(missing_exclude_files)
    missing_include_directories_set = set(missing_include_directories)
    missing_exclude_directories_set = set(missing_exclude_directories)
    files_to_include_set = set(files_to_include)
    files_to_exclude_set = set(files_to_exclude)

    return list(files_to_include_set - files_to_exclude_set)

