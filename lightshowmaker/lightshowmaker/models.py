from django.db import models
import json

class Show(models.Model):
    name = models.CharField(max_length=30)
    background = models.FileField(upload_to='images')
    steps = models.IntegerField(default=4)

    class Meta:
        ordering = 'name',
  
class Strand(models.Model):
    show = models.ForeignKey('Show', related_name='strands')
    name = models.CharField(max_length=30)
    eui64 = models.CharField(max_length=30)    

    class Meta:
        ordering = 'name',

class Lightbulb(models.Model):
    strand = models.ForeignKey('Strand', related_name='lightbulbs')
    number = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
    
    class Meta:
        ordering = 'strand__name', 'number',
        unique_together = ('strand', 'number'),

    def color_data(self):
        return json.dumps([{'red': color.red, 'green': color.green, 'blue': color.blue, 'alpha': color.brightness, 'color': color.rgba()} for color in self.colors.order_by('step')])
    
class BulbColor(models.Model):
    lightbulb = models.ForeignKey('Lightbulb', related_name='colors')
    step = models.IntegerField()
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    brightness = models.IntegerField()
    
    class Meta:
        ordering = 'lightbulb', 'step',
        unique_together = ('lightbulb', 'step'),
    
    def rgba(self):
        return 'rgba(%s, %s, %s, %s)' % (self.red * 17, self.green * 17, self.blue * 17, self.brightness / 255.0)
