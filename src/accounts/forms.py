from django import forms
from django.contrib.auth import (
                                    authenticate,
                                    get_user_model,
                                    login,
                                    logout,
                            )

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    """ we redefine the clean method of the form, we perform the check on user
    password - if nothing is wrong we call the clean of the super class meaning
    as the regular clean() method does """
    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # method to authenticate the user - return the user if exists
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("User does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Password is incorrect")
            if not user.is_active:
                raise forms.ValidationError("User is no longer active")
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Email address")
    email2 = forms.EmailField(label="Confirm Email address")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "email2",
            "password",
        ]

    """ code to user validation message on top of the form
    def clean(self, *args, **kwargs):
        print(self.cleaned_data)
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        print(email, email2)
        if email != email2:
            raise forms.ValidationError("Email do not match")
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("This email has already been used")
        return super(UserRegisterForm, self).clean(*args, **kwargs)"""

    # code to show ValidationError on the side of the control
    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email != email2:
            raise forms.ValidationError("Email do not match")
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("This email has already been used")
        return email
