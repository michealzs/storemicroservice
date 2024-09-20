from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm #,UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Return, SearchTerm, Coupon, ProductReview #UserProfile,
from django.utils import timezone
from django.core.exceptions import ValidationError


###################################################
#               UserProfile  Form                 #
###################################################
class UserProfileForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name','last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        if email and username and email != username:
            raise ValidationError("Username and email must match.")
        return cleaned_data

'''
class UserProfileForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address already in use')
        return cleaned_data
'''

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'


class UpdateUserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        if email and username and email != username:
            raise ValidationError("Username and email must match.")
        return cleaned_data


###################################################
#                Password Reset                   #
###################################################

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        #label="Email",
        max_length=254,
        #widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            #print("<========", self.request.META.get('HTTP_X_REAL_IP') , "tried email:", email, "========>")
            #raise forms.ValidationError("==> This email address is not associated with any account. <==")
            print("Non Exsistent Email Form")
        return email

###################################################
#                Return Form                    #
###################################################

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['order', 'reason_for_return', 'notes']
        widgets = {
            'order': forms.HiddenInput(),
            'reason_for_return': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

###################################################
#                Search Form                      #
###################################################

class SearchForm(forms.ModelForm):
    class Meta:
        model = SearchTerm
        fields = ['query']

###################################################
#                Cupon Form                      #
###################################################

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount', 'expiration_date', 'is_approved']

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data['expiration_date']
        if expiration_date < timezone.now():
            raise forms.ValidationError("Expiration date must be in the future.")
        return expiration_date

###################################################
#                ProductReview Form               #
###################################################

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['product', 'user', 'rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3})
        }