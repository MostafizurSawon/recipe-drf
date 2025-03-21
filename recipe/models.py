# models.py
from django.db import models
from django.core.exceptions import ValidationError
from users.models import User
from users.models import UserProfile

class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=40, unique=True)

    def __str__(self):
        return self.name

REACTION_CHOICES = [
    ('LIKE', 'Like'),
    ('WOW', 'Wow'),
    ('SAD', 'Sad'),
    ('LOVE', 'Love'),
]

class Recipe(models.Model):
    title = models.CharField(max_length=50)
    ingredients = models.TextField()
    category = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    img = models.URLField(null=True, blank=True)
    instructions = models.TextField()
    created_on = models.DateField(auto_now_add=True, null=True, blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_recipes', blank=True)

    def __str__(self):
        return f"{self.title} of Mr. {self.user.firstName} {self.user.lastName}"

    def get_reaction_counts(self):
        reactions = Reaction.objects.filter(recipe=self)
        return {
            'LIKE': reactions.filter(reaction_type='LIKE').count(),
            'WOW': reactions.filter(reaction_type='WOW').count(),
            'SAD': reactions.filter(reaction_type='SAD').count(),
            'LOVE': reactions.filter(reaction_type='LOVE').count(),
        }

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    reaction_type = models.CharField(max_length=4, choices=REACTION_CHOICES)

    class Meta:
        unique_together = [
            ('user', 'recipe'),  # One reaction per user per recipe
            ('user', 'comment'),  # One reaction per user per comment
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(recipe__isnull=False) | models.Q(comment__isnull=False),
                name='reaction_target_required'
            ),
            models.CheckConstraint(
                check=~models.Q(recipe__isnull=False, comment__isnull=False),
                name='reaction_single_target'
            )
        ]

    def __str__(self):
        target = self.recipe or self.comment
        return f"{self.user.firstName}'s {self.reaction_type} on {target}"

STAR_CHOICES = [
    ('⭐', '⭐'),
    ('⭐⭐', '⭐⭐'),
    ('⭐⭐⭐', '⭐⭐⭐'),
    ('⭐⭐⭐⭐', '⭐⭐⭐⭐'),
    ('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'),
]

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    rating = models.CharField(choices=STAR_CHOICES, max_length=10)

    class Meta:
        unique_together = ('reviewer', 'recipe')

    def clean(self):
        if Review.objects.filter(reviewer=self.reviewer, recipe=self.recipe).exists():
            raise ValidationError("You have already reviewed this recipe.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User: {self.reviewer.firstName} ; Recipe: {self.recipe.title}"

class Comment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')  # Add related_name='comments'
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content} Comment by {self.user.firstName} on {self.recipe.title}"

    def get_reaction_counts(self):
        reactions = Reaction.objects.filter(comment=self)
        return {
            'LIKE': reactions.filter(reaction_type='LIKE').count(),
            'WOW': reactions.filter(reaction_type='WOW').count(),
            'SAD': reactions.filter(reaction_type='SAD').count(),
            'LOVE': reactions.filter(reaction_type='LOVE').count(),
        }
        
    # def can_delete(self, requesting_user):
    #     """Check if the requesting user can delete this comment."""
    #     is_owner = self.recipe.user == requesting_user
    #     is_commenter = self.user == requesting_user
    #     is_staff = requesting_user.is_staff or requesting_user.is_superuser
    #     return (is_owner and not is_staff) or is_commenter or is_staff
    
    def can_delete(self, user):
        # Allow deletion if the user is the creator or an Admin
        return user == self.user or user.role == 'Admin'