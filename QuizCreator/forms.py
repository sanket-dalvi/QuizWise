from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField(label='Select an Excel file', help_text='Only Excel files are allowed.')

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx') and not file.name.endswith('.xls'):
            raise forms.ValidationError('File must be in Excel format (XLSX or XLS)')
        return file
