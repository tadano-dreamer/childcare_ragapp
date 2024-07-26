from django import forms
from .models import Student

class StudentForm(forms.Form):
    student_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'フルネームで書きましょう'}), label='児童の名前')
    record_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='記録日')
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': '対象児童の出来事や様子を記録しましょう'}), label='できごと')


class GptForm(forms.Form):
    student_name = forms.ModelChoiceField(
        queryset=Student.objects.values_list('student_name', flat=True).distinct(),
        label='児童の名前',
        empty_label="対象の児童を選択してください"
    )

class RagForm(forms.Form):
    rag_query = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'トピックを記入'}), label='トピック質問欄')