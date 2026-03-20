from django.db import models
from django.contrib.auth.models import User


# ---------------------- ROOMS ---------------------
class Room(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rooms/')
    capacity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default="Available")

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    check_in = models.DateField()
    check_out = models.DateField()
    payment_done = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="Booked")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.room.name}"

    @property
    def total_price(self):
        days = (self.check_out - self.check_in).days
        if days < 1:
            days = 1
        return self.room.price * days



# ---------------------- FEEDBACK ----------------------
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    rating = models.IntegerField(default=0)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rating}★)"

    # Admin માં star display માટે method
    def stars(self):
        return '⭐' * self.rating
    stars.short_description = 'Rating'


# ---------------------- CONTACT ----------------------
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ---------------------- GALLERY ----------------------
class GalleryImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="gallery/")  # ✅ Typo fix: gallary -> gallery
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ---------------------- BILL ----------------------
class Bill(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill for {self.reservation.name} - {self.reservation.room.name}"

# ---------------------- USER PROFILE ----------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, default='PayPal')  # Payment method
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.reservation.user.username}"