# Importing constants
from .constants import (
    SELECT_FILE_LABEL,
    ALLOWED_FILE_FORMAT,
    EXCEL_FORMAT_ERROR,
    EXCEL_EXTENSIONS,
)
from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField(label=SELECT_FILE_LABEL, help_text=ALLOWED_FILE_FORMAT)

    def clean_file(self):
        file = self.cleaned_data['file']
        if not any(file.name.endswith(ext) for ext in EXCEL_EXTENSIONS):
            raise forms.ValidationError(EXCEL_FORMAT_ERROR)
        return file
