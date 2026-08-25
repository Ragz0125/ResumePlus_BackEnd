
from typing import TypedDict


class EmailOutput(TypedDict):
    body: str
    subject: str
    
class EmailInput(TypedDict):
    body: str
    subject: str