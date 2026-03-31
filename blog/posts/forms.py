from django import forms

class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='',
        required=True,
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Enter a valid email — like you@example.com.',
        },
        widget=forms.EmailInput(attrs={"placeholder" : "you@domain.com", 
            "class": "w-full bg-panel/80 backdrop-blur-sm border border-line/60 rounded-full px-6 py-4 text-sm text-ink outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 transition-all shadow-inner placeholder:text-muted/60"}))
    