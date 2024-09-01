from django import forms
from .models import Quiz, Question, Option, Topic, User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuizForm(forms.ModelForm):

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'difficulty', 'topic', 'is_active', 'required_level', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'required_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Enter duration in minutes'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

OptionFormSet = forms.inlineformset_factory(
    Question, Option, form=OptionForm, extra=4, can_delete=True, max_num=4
)

class UserUpdateForm(UserChangeForm):
    email = forms.EmailField(disabled=True)  # Email cannot be changed

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture']

class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())