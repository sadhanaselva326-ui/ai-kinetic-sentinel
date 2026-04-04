class DocumentProcessingError(Exception):
    def __init__(self, message: str):
        self.message = message

class OCRFailureError(Exception):
    def __init__(self, message: str):
        self.message = message
        
class InvalidBase64Error(Exception):
    def __init__(self, message: str):
        self.message = message
