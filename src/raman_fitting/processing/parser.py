''' Parsing the data of spectrum into class instance '''


class Parser:
    
    _supported_suffixes = ['.txt']
    
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.choose_parsers()
        self.validate_data()
    
    
    @property
    def filepath(self):
        return self._filepath
    
    @filepath.setter
    def filepath(self, _fp):
        
        self.validate_fp(_fp)
    
    def validate_fp(self, _fp):
        _std_error_msg = f'Error in {self._class__} with file:{_fp}'
        
        if not _fp.is_file():
            raise ValueError(f'{self._std_error_msg} \n not a file.')
            
        if _fp.suffix not in self._supported_suffixes:
            raise ValueError(f'{_std_error_msg } \n Suffix "{self._suffix}" not in supported: {", ".join(self._supported_suffixes)}')
    
    def validate_data(self):
        if not all(self.ramanshift):
            pass
    
    def choose_parsers(self):
        
        if self._suffix == '.txt':
            self.parse_from_txt()
        
    def parse_from_txt(self, usecols=(0, 1), delimiter='\t', unpack=True, skiprows = 0):
        ramanshift, intensity= np.array([]),np.array([])
        i = skiprows
        while not ramanshift.any() and i < 2000:
            try:
                ramanshift, intensity = np.loadtxt(self.file, usecols=usecols, delimiter=delimiter, unpack=unpack, skiprows=i)
                self.ramanshift = ramanshift
                self.intensity = intensity
                # Alternative parsing method with pandas.read_csv
                # _rawdf = pd.read_csv(self.file, usecols=(0, 1), delimiter='\t', 
                #                     skiprows=i, header =None, names=['ramanshift','intensity'])
                print(self.file, len(ramanshift),len(intensity))
                self._skiprows = i
                self._read_succes = True
                self.spectrum_length = len(ramanshift)
                self.info.update({'spectrum_length' : self.spectrum_length,'_parser_skiprows' : i, '_parser_delim' : delimiter})
            except ValueError:
                i += 1
