import argparse
import pymanifest

ap = argparse.ArgumentParser()
pymanifest.add_args(ap)

args = ap.parse_args()
files = pymanifest.process_from_args(args)

print (files)
