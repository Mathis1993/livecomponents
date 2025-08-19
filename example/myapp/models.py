from functools import cached_property
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class CoffeeBean(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    origin = models.CharField(max_length=100, verbose_name="Origin")
    roast_level = models.CharField(max_length=50, verbose_name="Roast Level")
    flavor_notes = models.TextField(verbose_name="Flavor Notes")
    stock_quantity = models.PositiveIntegerField(
        verbose_name="Stock Quantity", default=0
    )

    def __str__(self):
        return self.name


class FloorPlanOrder(models.Model):
    class Dimension(models.TextChoices):
        TWO_DIMENSIONAL = "2D", "2D"
        THREE_DIMENSIONAL = "3D", "3D"

    class FurnitureStyle(models.TextChoices):
        ARCHAIC = "archaic", "Archaic"
        MODERN = "modern", "Modern"

    class Resolution(models.TextChoices):
        HD = "HD", "HD (1080p)"
        UHD = "UHD", "UHD (2160p)"

    class Country(models.TextChoices):
        AUSTRIA = "austria", "Austria"
        GERMANY = "germany", "Germany"
        SWITZERLAND = "switzerland", "Switzerland"

    PRICE_2D = 29.0
    PRICE_3D = 39.0
    SURCHARGE_UHD = 10.0

    dimension = models.CharField(max_length=255, choices=Dimension.choices)
    furniture_style = models.CharField(max_length=255, choices=FurnitureStyle.choices, null=True, default=None)
    resolution = models.CharField(max_length=255, choices=Resolution.choices, null=True, default=None)
    show_measurements = models.BooleanField(null=True, default=None)
    show_furniture = models.BooleanField(null=True, default=None)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    customer_first_name = models.CharField(max_length=255)
    customer_last_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    postcode = models.CharField(max_length=5)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255, choices=Country.choices)
    
    def save(self, *args, **kwargs):
        if self.dimension == self.Dimension.TWO_DIMENSIONAL:
            if self.resolution is None or self.show_furniture is None:
                raise ValidationError("resolution and show_furniture must be set for 2D dimension.")
            self.furniture_style = None
            self.show_measurements = None
        if self.dimension == self.Dimension.THREE_DIMENSIONAL:
            if self.furniture_style is None or self.show_measurements is None:
                raise ValidationError("furniture_style and show_measurements must be set for 3D dimension.")
            self.resolution = None
            self.show_furniture = None
        super().save(*args, **kwargs)

    @cached_property
    def unit_price(self) -> Optional[float]:
        if self.dimension == self.Dimension.TWO_DIMENSIONAL:
            if self.resolution == self.Resolution.UHD:
                return self.PRICE_2D + self.SURCHARGE_UHD
            return self.PRICE_2D
        if self.dimension == self.Dimension.THREE_DIMENSIONAL:
            return self.PRICE_3D
        return None

    @cached_property
    def total_price(self) -> float:
        quantity = self.quantity or 1
        unit_price = self.unit_price or 0.0
        return quantity * unit_price


class Country(models.Model):
    name = models.CharField(max_length=255)
