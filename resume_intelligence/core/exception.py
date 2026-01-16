# UnsupportedFileTypeError
# DocumentParseError
# EmptyDocumentError

class DocumentParseError(Exception):
    """Raised when a document cannot be parsed properly."""
    pass


class UnsupportedFileTypeError(Exception):
    """Raised when an unsupported file type is provided."""
    pass
