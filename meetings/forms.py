from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Meeting, MeetingParticipant
from Learner.models import get_db


class MeetingForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une réunion
    L'instructeur sélectionne les étudiants à inviter (depuis MongoDB)
    """
    students = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Étudiants à inviter",
        help_text="Sélectionnez les étudiants qui participeront à cette réunion"
    )
    
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'scheduled_date', 'duration']  # ✅ Exclure 'students' - géré manuellement
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Cours de Python avancé'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la réunion...'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 480,
                'step': 15,
                'value': 60
            }),
        }
        labels = {
            'title': 'Titre de la réunion',
            'description': 'Description',
            'scheduled_date': 'Date et heure',
            'duration': 'Durée (minutes)',
        }
        help_texts = {
            'scheduled_date': 'Sélectionnez une date et heure dans le futur',
            'duration': 'Durée en minutes (15 min minimum, 8h maximum)',
        }
    
    def __init__(self, *args, **kwargs):
        self.instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        
        # Récupérer les étudiants depuis MongoDB
        db = get_db()
        students_mongo = list(db.users.find({'role': 'student', 'is_active': True}))
        
        # Créer les choix pour le formulaire
        student_choices = []
        self.students_map = {}  # Pour mapper email -> User Django
        
        for student in students_mongo:
            email = student.get('email', '')
            username = student.get('username', '')
            first_name = student.get('first_name', '')
            last_name = student.get('last_name', '')
            
            # Créer un label lisible
            label = f"{first_name} {last_name}".strip() if first_name or last_name else username
            if email:
                label += f" ({email})"
            
            student_choices.append((email, label))
            
            # Créer ou récupérer l'utilisateur Django correspondant
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username or email.split('@')[0],
                    'first_name': first_name or '',
                    'last_name': last_name or '',
                }
            )
            self.students_map[email] = user
        
        # Définir les choix
        self.fields['students'].choices = student_choices
        
        # Si c'est une modification, pré-sélectionner les étudiants déjà invités
        if self.instance.pk:
            selected_emails = [user.email for user in self.instance.students.all()]
            self.fields['students'].initial = selected_emails
    
    def clean_scheduled_date(self):
        """Valide que la date est dans le futur"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date:
            if scheduled_date <= timezone.now():
                raise ValidationError(
                    "La date de la réunion doit être dans le futur."
                )
        return scheduled_date
    
    def clean_students(self):
        """Valide qu'au moins un étudiant est sélectionné"""
        students = self.cleaned_data.get('students')
        if not students or len(students) == 0:
            raise ValidationError(
                "Vous devez inviter au moins un étudiant à la réunion."
            )
        return students
    
    def save(self, commit=True):
        """Sauvegarde la réunion et ajoute les participants"""
        meeting = super().save(commit=False)
        
        # Définir l'instructeur si fourni
        if self.instructor:
            meeting.instructor = self.instructor
        
        if commit:
            meeting.save()
            
            # Si c'est une modification, supprimer les anciens participants
            if self.instance.pk:
                meeting.participants.all().delete()
            
            # Convertir les emails en objets User Django et créer les participants
            student_emails = self.cleaned_data.get('students')
            students = [self.students_map[email] for email in student_emails if email in self.students_map]
            
            # Créer les MeetingParticipant pour chaque étudiant
            # Note: Le ManyToManyField 'students' utilise through='MeetingParticipant'
            # donc la relation est automatiquement gérée lors de la création des MeetingParticipant
            for student in students:
                MeetingParticipant.objects.create(
                    meeting=meeting,
                    student=student,
                    status='invited'
                )
        
        return meeting


class MeetingUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier une réunion existante
    Ne permet pas de modifier la date si la réunion a déjà commencé
    """
    students = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Étudiants à inviter"
    )
    
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'scheduled_date', 'duration']  # ✅ Exclure 'students' - géré manuellement
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 480,
                'step': 15
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Récupérer les étudiants depuis MongoDB
        db = get_db()
        students_mongo = list(db.users.find({'role': 'student', 'is_active': True}))
        
        # Créer les choix pour le formulaire
        student_choices = []
        self.students_map = {}
        
        for student in students_mongo:
            email = student.get('email', '')
            username = student.get('username', '')
            first_name = student.get('first_name', '')
            last_name = student.get('last_name', '')
            
            label = f"{first_name} {last_name}".strip() if first_name or last_name else username
            if email:
                label += f" ({email})"
            
            student_choices.append((email, label))
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username or email.split('@')[0],
                    'first_name': first_name or '',
                    'last_name': last_name or '',
                }
            )
            self.students_map[email] = user
        
        self.fields['students'].choices = student_choices
        
        # Pré-remplir les étudiants
        if self.instance.pk:
            selected_emails = [user.email for user in self.instance.students.all()]
            self.fields['students'].initial = selected_emails
            
            # Si la réunion a commencé, désactiver la modification de la date
            if self.instance.status != 'scheduled':
                self.fields['scheduled_date'].disabled = True
                self.fields['scheduled_date'].help_text = "La date ne peut pas être modifiée car la réunion a déjà commencé"
    
    def clean_scheduled_date(self):
        """Valide que la date est dans le futur et que la réunion n'a pas commencé"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if self.instance.status != 'scheduled':
            # Ne pas valider si la réunion a déjà commencé
            return self.instance.scheduled_date
        
        if scheduled_date and scheduled_date <= timezone.now():
            raise ValidationError(
                "La date de la réunion doit être dans le futur."
            )
        
        return scheduled_date


class MeetingFilterForm(forms.Form):
    """Formulaire pour filtrer les réunions"""
    STATUS_CHOICES = [
        ('all', 'Toutes'),
        ('scheduled', 'Planifiées'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminées'),
        ('cancelled', 'Annulées'),
    ]
    
    TIME_CHOICES = [
        ('all', 'Toutes les dates'),
        ('upcoming', 'À venir'),
        ('past', 'Passées'),
        ('today', "Aujourd'hui"),
        ('week', 'Cette semaine'),
        ('month', 'Ce mois'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    time_filter = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par titre...'
        })
    )
