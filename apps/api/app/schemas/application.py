from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ApplicationFieldType(str, Enum):
    text = "text"
    textarea = "textarea"
    email = "email"
    tel = "tel"
    url = "url"
    select = "select"
    radio = "radio"
    checkbox = "checkbox"
    date = "date"
    file = "file"
    unknown = "unknown"


class Validation(BaseModel):
    pattern: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None


class SelectOption(BaseModel):
    value: str
    label: str


class ApplicationField(BaseModel):
    key: str
    label: str
    type: ApplicationFieldType
    required: bool
    options: Optional[List[SelectOption]] = None
    validation: Optional[Validation] = None
    source_hint: Optional[str] = None
