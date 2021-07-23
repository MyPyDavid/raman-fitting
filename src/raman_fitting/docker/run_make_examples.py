"""
Created on Thu Jul 22 11:45:34 2021

@author: DW

For this to work, the app needs be installed inside the docker container

"""
from time import sleep

# import raman_fitting
from .api import make_examples

# from ..api import make_examples

if __name__ == "__main__":
    print(
        'Hello Docker World, the raman_fitting "make examples" command from the containter is starting in 3 seconds...'
    )
    sleep(2)
    print("\n...and Go!.....\n")
    make_examples()
