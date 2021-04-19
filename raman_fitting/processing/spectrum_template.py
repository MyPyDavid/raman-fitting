#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple

class Spectrum():
    
    def __init__(self, spec_name = 'spectrum_info'):
        self.spec_name = spec_name
        self.grp_names()
        self.set_template()
    

    def grp_names(self):
        sGrp_cols = ('SampleGroup', 'SampleID', 'FileCreationDate')
        sPos_cols = ('FileStem','SamplePos','FilePath')
        spectrum_cols = ('ramanshift', 'intensity_raw', 'intensity')
        spectrum_info_cols = ('spectrum_length',)
        export_info_cols  = ('DestGrpDir', 'DestFittingPlots', 'DestFittingComps', 'DestRaw' )
        info_cols = sGrp_cols+ sPos_cols + spectrum_cols + spectrum_info_cols + export_info_cols
        names = {'sGrp_cols' : sGrp_cols,'sPos_cols' : sPos_cols, 'spectrum_cols' : spectrum_cols,
                 'spectrum_info_cols' : spectrum_info_cols,'export_info_cols' : export_info_cols, 'all' : info_cols}
        Names = namedtuple('GrpNames', names.keys())
#        output_ary = np.array(output)   # this is your matrix 
#        output_vec = output_ary.ravel() # this is your 1d-array
        self.grp_names =  Names(**names)
    
    def set_template(self):
        # name = 'spectrum_info'
        self.template = namedtuple(self.spec_name, self.grp_names.all)