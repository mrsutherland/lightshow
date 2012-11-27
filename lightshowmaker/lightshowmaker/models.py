from django.db import models

class Show(models.Model):
    name = models.CharField(max_length=30)
    background = models.FileField(upload_to='images')
    
class Lightbulb(models.Model):
    show = models.ForeignKey('Show')
    strand = models.IntegerField(default=1)
    number = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
    
class BulbColor(models.Model):
    bulb = models.ForeignKey('Lightbulb')
    frame = models.IntegerField()
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    brightness = models.IntegerField()