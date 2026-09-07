class PydanticParseError(Exception):
    pass
class PydanticParseTypeError(TypeError, PydanticParseError):
    pass

class PydanticParseValueError(ValueError, PydanticParseError):
    pass