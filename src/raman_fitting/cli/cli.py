#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import argparse


def _testing():
    args = parser.parse_args(['-M', 'debug'])

def main():
    
    '''
    The command line interface for raman_fitting
    '''
    
    
    parser = argparse.ArgumentParser(
        description='Command-line interface for raman_fitting package main.'
        )
    
    parser.add_argument(
        '-M', '--run-mode', 
        type=str, 
        choices=['normal','testing','debug'],
        help='running mode of package, for testing',
        default='normal'
    )
    
    parser.add_argument(
        '-sIDs', '--sampleIDs',
        nargs='+',
        default=[],
        help='Selection of names of SampleIDs from index to run over.'
    )
    
    parser.add_argument(
        '-sGrps', '--samplegroups',
        nargs='+',
        default=[],
        help='Selection of names of sample groups from index to run over.'
    )
    
    
    # Execute the parse_args() method
    args = parser.parse_args()
    
    # import the raman_fitting package
    import raman_fitting as rf
    
    
    print(f'CLI args: {args}')
    if args.run_mode == 'normal':
        
        
        # _org_index = OrganizeRamanFiles()
        # RL = RamanLoop(_org_index, run_mode ='normal')
        _main_run = rf.MainDelegator(**vars(args))
    
    if args.run_mode.upper() == 'DEBUG':
        args.run_mode = args.run_mode.upper() 
        
        _main_run = rf.MainDelegator(**vars(args))


    
    if 'yes' == 'n':
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
