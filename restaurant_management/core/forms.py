from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User


class RegistrationForm(UserCreationForm):
    """Formulaire d'inscription avec sélection de rôle"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro de téléphone'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse',
            'rows': 3
        })
    )
    
    role = forms.ChoiceField(
        choices=User.USER_ROLES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'role-select'
        })
    )
    
    # Champs supplémentaires pour les restaurants
    restaurant_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control restaurant-field',
            'placeholder': 'Nom du restaurant'
        })
    )
    
    cuisine_type = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control restaurant-field'
        })
    )
    
    # Champs supplémentaires pour les livreurs
    vehicle_type = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control livreur-field'
        })
    )
    
    license_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control livreur-field',
            'placeholder': 'Numéro de permis'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Import ici pour éviter les imports circulaires
        from restaurant.models import Restaurant
        from livreur.models import DeliveryPersonProfile
        
        # Définir les choix pour cuisine_type
        self.fields['cuisine_type'].choices = Restaurant.CUISINE_TYPES
        
        # Définir les choix pour vehicle_type
        self.fields['vehicle_type'].choices = DeliveryPersonProfile.VEHICLE_TYPES
        
        # Ajouter des classes CSS aux champs par défaut
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Validation spécifique pour les restaurants
        if role == 'restaurant':
            if not cleaned_data.get('restaurant_name'):
                raise forms.ValidationError("Le nom du restaurant est requis.")
            if not cleaned_data.get('cuisine_type'):
                raise forms.ValidationError("Le type de cuisine est requis.")
        
        # Validation spécifique pour les livreurs
        if role == 'livreur':
            if not cleaned_data.get('vehicle_type'):
                raise forms.ValidationError("Le type de véhicule est requis.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
            
            # Créer les profils spécifiques selon le rôle
            self._create_role_specific_profile(user)
        
        return user
    
    def _create_role_specific_profile(self, user):
        """Créer le profil spécifique selon le rôle de l'utilisateur"""
        
        if user.role == 'client':
            from client.models import CustomerProfile
            CustomerProfile.objects.create(user=user)
            
        elif user.role == 'restaurant':
            from restaurant.models import Restaurant
            Restaurant.objects.create(
                owner=user,
                name=self.cleaned_data['restaurant_name'],
                description=f"Restaurant {self.cleaned_data['restaurant_name']}",
                cuisine_type=self.cleaned_data['cuisine_type'],
                address=user.address or '',
                phone=user.phone or '',
                email=user.email,
                opening_time='08:00',
                closing_time='22:00'
            )
            
        elif user.role == 'livreur':
            from livreur.models import DeliveryPersonProfile
            DeliveryPersonProfile.objects.create(
                user=user,
                vehicle_type=self.cleaned_data['vehicle_type'],
                license_number=self.cleaned_data.get('license_number', '')
            )


class LoginForm(forms.Form):
    """Formulaire de connexion"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur ou email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Permettre la connexion avec email ou nom d'utilisateur
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    raise forms.ValidationError("Identifiants incorrects.")
            
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Identifiants incorrects.")
            if not user.is_active:
                raise forms.ValidationError("Ce compte est désactivé.")
            
            self.user = user
        
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email