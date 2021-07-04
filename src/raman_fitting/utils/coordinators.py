from collections import OrderedDict
from warnings import warn


class FieldsTrackerWarning(UserWarning):
    pass


class FieldsTracker:
    """
    Keeps check of the fields from multiple sources,
    allows to store values in dict
    yields results a single results from several sources for each field
    status is True when all fields in results have at least one value
    """

    def __init__(self, fields: list = [], sources: tuple = [], **kwargs):
        self.fields = fields
        self.sources = sources
        self._register_template = self.make_register(sources, fields)
        self.set_sources_attr()
        self._results = {}

    def make_register(self, sources, fields):
        _reg = {source: {field: None for field in fields} for source in sources}
        return _reg

    def set_sources_attr(self):
        for source in self.sources:
            setattr(self, f"{source}", self._register_template[source])

    @property
    def register(self):
        _reg = {source: getattr(self, source) for source in self.sources}
        return _reg

    @property
    def status(self):
        _st = False
        if set(self.results) == set(self.fields):
            _st = True
        return _st

    @property
    def results(self):
        return self._results

    def _set_results(self):
        _results = self.get_values_from_all_fields()
        self._results = _results

    @property
    def missing(self):
        results = self.results
        _missing = set(self.fields) - set(results.keys())
        return _missing

    def get_values_from_all_fields(self):
        _result_values = {}
        for field in self.fields:
            _fvaldict_sources = self.get_field_value_from_sources(field)
            if _fvaldict_sources:
                _src = {"source": i for i in _fvaldict_sources.keys()}
                _value = {"value": i for i in _fvaldict_sources.values()}
                _nice_result = {**_src, **_value}
                _result_values.update({field: _nice_result})
        return _result_values

    def get_field_value_from_sources(self, field):
        _fsvals = OrderedDict({})
        _result = {}
        for source in self.sources:
            _src = getattr(self, source)
            _fval = _src.get(field, None)
            if _fval:
                _fsvals.update({source: _fval})
        # if _fsvals:
        #     if not dict in map(type, _fsvals.values()):
        #         breakpoint()
        #         _setvals = set(_fsvals.values())
        #     else:
        _setvals = _fsvals.values()
        _setsources = set(_fsvals.keys())
        _lstsources = list(_setsources)
        if len(_setvals) == 1:
            _fval = list(_setvals)[0]
            if len(_setsources) == 1:
                _src = _lstsources[0]
            elif len(_setsources) > 1:
                _src = list(_fsvals.keys())[0]
                warn(
                    f"Field {field} has multiple sources {_setsources}, one value ",
                    FieldsTrackerWarning,
                )
            _result = {_src: _fval}
        elif len(_setvals) > 1:
            # breakpoint()
            _firstval = list(_fsvals.items())[0]
            warn(
                f"Field {field} has multiple sources {_setsources}, different values follow order of sources ",
                FieldsTrackerWarning,
            )
            _result = {_firstval[0]: _firstval[1]}
        return _result

    def multi_store(self, source: str, **kwargs):
        # _fields_dict = {k: val for k, val in _dict.items() if k in self.fields}
        _fields_kwargs = {k: val for k, val in kwargs.items() if k in self.fields}
        # _input_dict = {**_fields_kwargs, **_fields_dict}
        if _fields_kwargs:
            for field, val in _fields_kwargs.items():
                self.store(source, field, val)
            self._set_results()

    def store(self, source, field, val):
        """store one value: source, field, val"""
        if source in self.sources and field in self.fields and val:
            _src = getattr(self, source)
            _fval = _src.get(field, None)
            if not _fval:
                _src[field] = val
            elif _fval == val:
                warn(
                    f"Redefinition of {field} in {source} ignored",
                    FieldsTrackerWarning,
                )
            elif _fval != val:
                _src[field] = val
                warn(
                    f"Overwriting of {field} in {source} with new value! {_fval} is not {val}",
                    FieldsTrackerWarning,
                )
            else:
                warn(f"Store {source} {val} unexpected", FieldsTrackerWarning)

            setattr(self, source, _src)
            self._set_results()
        else:
            warn(
                f"Store in {source} at {field} not in {self.sources} or not in {self.fields} or not {val}, ignored.",
                FieldsTrackerWarning,
            )
            pass  # store values not recognized
