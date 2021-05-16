#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import argparse


def MainParser():
    
    '''
    The command line interface for raman_fitting
    '''
    
    
    parser = argparse.ArgumentParser(description='Command line interface for raman_fitting package main.')
    
    parser.add_argument('-M', '--run-mode', type=str, 
                        help='running mode of package, for testing',
                        choices=['normal','testing','debug'],
                        default='normal')
    
    parser.add_argument('-sIDs', '--sampleIDs', nargs='+',
                    help='Selection of names of SampleIDs from index to run over.', default=[])
    
    parser.add_argument('-sGrps', '--samplegroups', nargs='+',
                    help='Selection of names of sample groups from index to run over.', default=[])
    
    
    # Execute the parse_args() method
    args = prs.parse_args()

    # import pygaps as pg
    
    
     runq = 'n'
    
    if runq == 'n':
        pass
        
    else:
        ROrg = OrganizeRamanFiles()
        if 'y' in runq:
            RamanIndex_all = ROrg.index
            RamanIndex = index_selection(RamanIndex_all,run= runq,groups=['DW'])
            RL = RamanLoop(RamanIndex, run_mode ='normal')
            # self = RL
        elif 'test' in runq:
            RamanIndex_all = ROrg.index
            RamanIndex = index_selection(RamanIndex_all,run= runq,groups=[])
            RL = RamanLoop(RamanIndex, run_mode ='DEBUG')
            self = RL
            
        else:
            try:
                if not RamanIndex.empty:
                    print('Raman Index ready')
            except:
                print('Raman re-indexing')
                RamanIndex_all = ROrg.index
                
                RamanIndex = index_selection(RamanIndex_all,groups=[])
    
    
    
    return parser
