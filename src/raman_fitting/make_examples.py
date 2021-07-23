"""
Created on Thu Jul 22 16:19:28 2021

@author: DW
"""
from time import sleep
from delegator.main_delegator import MainDelegator


def make_examples():
    _main_run = MainDelegator(run_mode="make_examples")


if __name__ == "__main__":
    print(
        'Hello Docker World, the raman_fitting "make examples" command from the containter is starting in 3 seconds...'
    )
    sleep(2)
    print("\n...and Go!.....\n")
    make_examples()
