from django import forms
from .models import ReponseQuestionnaire

class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = ReponseQuestionnaire
        fields = '__all__'
