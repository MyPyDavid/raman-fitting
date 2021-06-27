
from pathlib import Path
import hashlib

import pandas as pd

import logging

logger = logging.getLogger('raman_fitting')


class PathParser(Path):

    _flavour = type(Path())._flavour

    _sID_name_mapper = {'David': 'DW',
                        'stephen': 'SP',
                        'Alish': 'AS',
                        'Aish': 'AS'}
    _reference_sID = 'Si-ref'

    index_file_path_keys = ('FileStem','FilePath')
    index_file_sample_keys = ('SampleID','SamplePos','SampleGroup')
    index_file_stat_keys = ('FileCreationDate', 'FileCreation','FileModDate', 'FileMod', 'FileSize')
    index_file_read_text_keys = ('FileHash', 'FileText')

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qcnm = self.__class__.__qualname__

        self.stats_ = None

        self.parse_result = self.collect_parse_results()

    def collect_parse_results(self):
        ''' performs all the steps for parsing the filepath'''
        parse_res_collect = {}
        if self.exists():
            if self.is_file():
                self.stats_ = self.stat()
                _filepath = self.parse_filepath()
                _sample = self.parse_sample_with_checks()
                _filestats = self.parse_filestats()
                _read_text= self.parse_read_text()
                parse_res_collect = {**_filepath, **_sample, **_filestats, **_read_text}
            else:
                logger.warning(f'{self._qcnm} {self} is not a file => skipped')
        else:
            logger.warning(f'{self._qcnm} {self} does not exist => skipped')
        return parse_res_collect

    def parse_filepath(self):
        # FIX ME store fullpath in a str or not?
        _parse_res = (self.stem, self)
        return self.make_dict_from_keys('index_file_path_keys', _parse_res)

    def parse_sample_with_checks(self):
        ''' parse the sID, position and sgrpID from stem'''
        _parse_res  = ()
        _parse_res = self._extra_sID_check_if_reference()
        if not _parse_res:
             _parse_res = self.parse_filepath_to_sid_and_pos(self.stem)
        if len(_parse_res) ==2:
            sID, position = _parse_res
            sgrpID = self._extra_get_sgrpID_from_sID(sID)
            _parse_res = sID, position, sgrpID

        return self.make_dict_from_keys('index_file_sample_keys', _parse_res)


    def _extra_get_sgrpID_from_sID(self, sID):
        ''' adding the extra sample Group key from sample ID'''
        _maxalphakey = min([n for n,i in enumerate(sID) if not str(i).isalpha()], default=0)
        sgrpID = ''.join([i for i in sID[0:_maxalphakey] if i.isalpha()])
        if hasattr(self, 'parts'):
            sgrpID = self._extra_sgrID_overwrite_from_parts(sgrpID)
        return sgrpID

    def _extra_sgrID_overwrite_from_parts(self, sgrpID):

        if 'Raman Data for fitting David' in self.parts:
             sgrpID = 'SH'
        return sgrpID

    def _extra_sID_overwrite_from_mapper(self, sID):

        if hasattr(self, '_sID_name_mapper'):
            if self._sID_name_mapper:
                _sID_map = self._sID_name_mapper.get(sID, None)
                if _sID_map:
                    sID = _sID_map
        return sID

    def _extra_sID_check_if_reference(self, ref_ID = 'Si-ref'):

        if ref_ID in self.stem:
            position = 0
            sID = 'Si-ref'
            return (sID, position)
        else:
            return None

    def parse_filepath_to_sid_and_pos(self,
                                      seps = ('_', ' ', '-')
                                      ):
        '''
        Parser for the filenames -> finds SampleID and sample position

        Parameters
        ----------
        # ramanfile_stem : str
        #    The filepath which the is parsed
        seps : tuple of str default
            ordered collection of seperators tried for split
            default : ('_', ' ', '-')

        Returns
        -------
        tuple of strings
            Collection of strings which contains the parsed elements.
        '''

        split = None

        first_sep_match_index =-min([n for n,i in enumerate(seps) if i in self.stem],default=None)

        first_sep_match = seps[first_sep_match_index] if first_sep_match_index  else None

        split = self.stem.split(first_sep_match)

        if len(split) == 1:
            sID = split[0]
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
            sID = '_'.join(split[0:-1])
            position = int(''.join(filter(str.isdigit,split[-1])))
#                split =[split_Nr0] + [position]
        elif  len(split) == 0:
            sID = split[0]
            position = 0
        else:
            sID = split[0] # default take split[0]
            if ''.join(((filter(str.isdigit,split[-1])))) == '':
                position = 0
            else:
                position = int(''.join(filter(str.isdigit,split[-1])))

        RF_row_sIDs_out = (sID, position)
        return RF_row_sIDs_out

    def parse_read_text(self, max_bytes = 10**6):
        ''' read text introspection into files, might move this to a higher level'''
        _text = ''
        if self.stats_.st_size < max_bytes:
            try:
                _text = self.read_text(encoding='utf-8')
            except Exception as e:
                _text - 'read_error'
                logger.warning(f'{self._qcnm} file read text error => skipped.\n{e}')
        else:
            _text = 'max_size'
            logger.warning(f'{self._qcnm} file too large => skipped')

        filehash = hashlib.md5(_text.encode('utf-8')).hexdigest()
        filetext = _text
        return self.make_dict_from_keys('index_file_read_text_keys', (filehash, filetext))


    def parse_filestats(self):
        ''' get status metadata from a file'''
        fstat = self.stats_

        ct, mt = pd.to_datetime(fstat.st_ctime,unit='s'), pd.to_datetime(fstat.st_mtime,unit='s')
        ct_date, mt_date = ct.date(),mt.date()

        filestat_out = ct_date, ct, mt_date, mt, fstat.st_size
        return self.make_dict_from_keys('index_file_stat_keys', filestat_out)
        # if len(self.index_file_stat_keys) == len(filestat_out):
        #     filestat_out =  dict(zip(self.index_file_stat_keys, filestat_out))
        # return filestat_out

    def make_dict_from_keys(self, _keys_attr: str, _result: tuple):
        ''' returns dict from tuples of keys and results'''
        _keys = ()
        if hasattr(self, _keys_attr):
            _keys = getattr(self, _keys_attr)
        if not len(_result) == len(_keys):
            # if len not matches make stand in numbered keys
            _keys = [f'{_keys_attr}_{n}' for n,i in enumerate(_result)]
        return dict(zip(_keys, _result))

        # return filestat_out
