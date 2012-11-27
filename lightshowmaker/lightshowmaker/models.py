from django.db import models
import json

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
    
    def color_data(self):
        return json.dumps([{'red': color.red, 'green': color.green, 'blue': color.blue, 'color': color.rgb()} for color in self.colors.order_by('step')])
    
class BulbColor(models.Model):
    lightbulb = models.ForeignKey('Lightbulb', related_name='colors')
    step = models.IntegerField()
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    brightness = models.IntegerField()
    
    def rgb(self):
        return 'rgb(%s, %s, %s)' % (self.red * 17, self.green * 17, self.blue * 17)
