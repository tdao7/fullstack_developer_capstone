from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CarMake(models.Model):
 name = models.CharField(max_length=100, unique=True)
 description = models.TextField(blank=True)
 def __str__(self): return self.name

class CarModel(models.Model):
 class VehicleType(models.TextChoices):
  SEDAN = 'Sedan', 'Sedan'
  SUV = 'SUV', 'SUV'
  COUPE = 'Coupe', 'Coupe'
  WAGON = 'Wagon', 'Wagon'
 make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
 name = models.CharField(max_length=100)
 type = models.CharField(max_length=15, choices=VehicleType.choices)
 year = models.IntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2035)])
 class Meta: unique_together = ('make','name','year')
 def __str__(self): return f'{self.make} {self.name} {self.year}'

class Review(models.Model):
 dealership = models.PositiveIntegerField(db_index=True)
 name = models.CharField(max_length=120)
 purchase = models.BooleanField(default=False)
 purchase_date = models.DateField(null=True, blank=True)
 review = models.TextField()
 car_make = models.CharField(max_length=100, blank=True)
 car_model = models.CharField(max_length=100, blank=True)
 car_year = models.PositiveIntegerField(null=True, blank=True)
 sentiment = models.CharField(max_length=20, default='neutral')
 created_at = models.DateTimeField(auto_now_add=True)
 def __str__(self): return f'{self.name} on dealer #{self.dealership}'
