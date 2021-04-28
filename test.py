import argparse
import pymanifest

cust_arg_map = dict(pymanifest.DEFAULT_ARG_MAP)
cust_arg_map['--recurse-directory'] = '--recurse-so-directory'
cust_arg_map['--pattern'] = '--so-pattern'

ap = argparse.ArgumentParser()
pymanifest.add_args(ap, cust_arg_map)

args = ap.parse_args()
files = pymanifest.process_from_args(args, cust_arg_map)

print (files)
