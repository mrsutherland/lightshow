from django.db import models

class Show(models.Model):
    name = models.CharField(max_length=30)
    background = models.FileField(upload_to='images')
    
class Strand(models.Model):
    show = models.ForeignKey('Show', related_name='strands')
    name = models.CharField(max_length=30)
    eui64 = models.CharField(max_length=30)    

class Lightbulb(models.Model):
    strand = models.ForeignKey('Strand', related_name='lightbulbs')
    number = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
    
class BulbColor(models.Model):
    lightbulb = models.ForeignKey('Lightbulb', related_name='colors')
    frame = models.IntegerField()
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    brightness = models.IntegerField()
