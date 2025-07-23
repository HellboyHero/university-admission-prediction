from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class College(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=100, default='United States')
    description = models.TextField(blank=True)
    acceptance_rate = models.FloatField()
    ranking = models.IntegerField()
    tuition = models.FloatField(default=0)
    student_faculty_ratio = models.FloatField(default=0)
    total_enrollment = models.IntegerField(default=0)
    average_gre = models.FloatField(default=0)
    average_toefl = models.FloatField(default=0)
    min_gre_score = models.IntegerField(default=290)  # Adding minimum GRE score
    min_toefl_score = models.IntegerField(default=80)  # Adding minimum TOEFL score
    min_cgpa = models.FloatField(default=3.0)  # Adding minimum CGPA
    website = models.URLField(blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_colleges', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['country', 'ranking']

class AdmissionPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    gre_score = models.IntegerField()
    toefl_score = models.IntegerField()
    cgpa = models.FloatField()
    research_experience = models.BooleanField(default=False)
    sop = models.FloatField()  # Statement of Purpose score (1-5)
    lor = models.FloatField()  # Letter of Recommendation score (1-5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Prediction for {self.user.username if self.user else "Anonymous"}'

    def calculate_chance(self):
        # Simple weighted calculation
        gre_weight = 0.3
        toefl_weight = 0.2
        cgpa_weight = 0.3
        research_weight = 0.1
        sop_weight = 0.05
        lor_weight = 0.05

        # Normalize scores
        gre_norm = min(1, self.gre_score / 340)
        toefl_norm = min(1, self.toefl_score / 120)
        cgpa_norm = min(1, self.cgpa / 4.0)
        research_norm = 1 if self.research_experience else 0
        sop_norm = self.sop / 5
        lor_norm = self.lor / 5

        # Calculate weighted sum
        chance = (
            gre_norm * gre_weight +
            toefl_norm * toefl_weight +
            cgpa_norm * cgpa_weight +
            research_norm * research_weight +
            sop_norm * sop_weight +
            lor_norm * lor_weight
        ) * 100

        return round(chance, 2)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='profile_images/default.png', upload_to='profile_images', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    interests = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar and hasattr(self.avatar, 'path') and self.avatar.path:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except (FileNotFoundError, IOError):
                # If the file doesn't exist or can't be opened, skip image processing
                pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class AdmissionData(models.Model):
    gre_score = models.IntegerField()
    toefl_score = models.IntegerField()
    cgpa = models.FloatField()
    research_experience = models.BooleanField(default=False)
    sop = models.FloatField()  # Statement of Purpose score (1-5)
    lor = models.FloatField()  # Letter of Recommendation score (1-5)
    university_ranking = models.IntegerField()
    university_acceptance_rate = models.FloatField()
    admitted = models.BooleanField()  # Target variable: 1 if admitted, 0 if rejected
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Admission Data #{self.id} - {"Admitted" if self.admitted else "Rejected"}'

    class Meta:
        ordering = ['-created_at']
