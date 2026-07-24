#Fractalis Oneiricus - Central Application

import os
import sys
sys.path.append('../../shared_space/compendium/')

from fractalis_oneiricus_core import execute_script

if __name__ == '__main__':
    print('Starting Fractalis Oneiricus...')
    execute_script('../../shared_space/compendium/fractalis_oneiricus_core.py')