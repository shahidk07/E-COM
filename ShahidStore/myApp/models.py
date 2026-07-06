from django.db import models

# Create your models here.

##create a table named Product,This class inherits the Model from models package
#providing necessary methods like .save(), .delete().etc;

class Product(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
    image_url=models.URLField(max_length=1000)
    price=models.DecimalField(max_digits=7,decimal_places=3)
    category=models.CharField(max_length=50,default="uncategorized")
    stock=models.PositiveIntegerField(default=10)
    created_at=models.DateTimeField(auto_now_add=True)

'''
What is __str__?
It's a special Python method that tells Python:
"If someone tries to print this object, what text should I show?"
'''
def __str__(self):
    return self.name

'''blank=True
Allows users to leave the field empty in forms/admin.

null=True
Allows the database to store: NULL'''

   
   