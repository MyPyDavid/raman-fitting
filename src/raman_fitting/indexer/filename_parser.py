

def parse_filepath_to_sid_and_pos(ramanfilepath):
    ''' Parser for the filenames -> finds SampleID and sample position '''
    ramanfile_stem  = ramanfilepath.stem

    if '_'  in ramanfile_stem:
        split = ramanfile_stem.split('_')
    elif ' ' in ramanfile_stem:
        split = ramanfile_stem.split(' ')
    else:
#            print(ramanfile_stem)
        split = ramanfile_stem.split('_')

    if 'SI' in ramanfile_stem.upper() or 'Si-ref' in ramanfile_stem: 
        position = 0
        sID = 'Si-ref'
    else:
        if len(split) == 1:
            sID = [SampleIDstr(split[0]).SampleID][0]
            position = 0
        elif len(split) == 2:
            sID = split[0]
            _pos_strnum = ''.join(i for i in split[1] if i.isnumeric())
            if _pos_strnum:
                position = int(_pos_strnum)   
            else:
                position = split[1]

#                split = split + [0]
        elif len(split) >= 3:
            sID = [SampleIDstr('_'.join(split[0:-1])).SampleID][0]
            position = int(''.join(filter(str.isdigit,split[-1])))
#                split =[split_Nr0] + [position]
        elif  len(split) == 0:
            sID = SampleIDstr(split).SampleID
            position = 0
        else:
            sID = [SampleIDstr(split[0]).SampleID][0]
            if ''.join(((filter(str.isdigit,split[-1])))) == '':
                sID = [ramanfile_stem]
                position = 0
            else:
                position = int(''.join(filter(str.isdigit,split[-1])))
    sGrpID = ''.join([i for i in sID[0:3] if i.isalpha()])
    if 'Raman Data for fitting David' in ramanfilepath.parts:
        sGrpID = 'SH'    
    RF_row_sIDs_out = (ramanfile_stem, sID, position, sGrpID, ramanfilepath)
    return RF_row_sIDs_out


class SampleIDstr:
    """Tools to find the SampleID in a string"""
    
    _std_names = [('David','DW'), ('stephen','SP'), 
                  ('Alish','AS'), ('Aish','AS')]
    
    def __init__(self,string):
        self.SampleID = self.name_to_sampleid(string)
       
    def name_to_sampleid(self,string):
        for i,sID in self._std_names:
            if i in string:
                string = string.replace(i,sID)
        return string
