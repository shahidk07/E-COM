import json
import random

from django.core.management.base import BaseCommand
from myApp.models import Product

class Command(BaseCommand):
    help="import products from JSON"
    
    def handle(self, *args, **kwargs):
        with open("products.json","r") as f:
            products=json.load(f)
        created=0

        for item in products:

            Product.objects.create(
            name=item["name"],
            description=item["description"],
            image_url=item["image_url"],
            category=item["category"],
            price=random.randint(0,9999),
            stock=random.randint(1, 50),)
            
            created+=1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported {created} products"
                )
            )