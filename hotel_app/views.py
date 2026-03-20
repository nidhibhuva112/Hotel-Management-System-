from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Room, Reservation, Feedback, Contact, GalleryImage, Bill, Payment
from .forms import ReservationForm, ReservationUpdateForm, FeedbackForm, ContactForm, RoomForm

# Admin Credentials (fixed)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@123'

# ----------------- FRONTEND -------------------

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def rooms(request):
    all_rooms = Room.objects.all()
    return render(request, 'rooms.html', {'rooms': all_rooms})

def restaurant(request):
    return render(request, 'restaurant.html')

def feedback_view(request):
    # 🔒 Only logged-in users can access
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user   # Save which user gave feedback
            feedback.save()
            return redirect('feedback')
    else:
        form = FeedbackForm()

    all_feedbacks = Feedback.objects.all().order_by('-created_at')

    return render(
        request,
        'feedback.html',
        {
            'form': form,
            'feedbacks': all_feedbacks,
            'stars': range(1, 6)   # ⭐ For star rating display
        }
    )



def contact(request):
    if not request.user.is_authenticated:   # ✅ Session check
        return redirect('login')

    owner_info = {
        'name': 'Ms. Nidhi Bhuva',
        'role': 'Owner',
        'photo': 'images/person_1.jpg',
        'email': 'nidhi12@suryagardenhotel.com',
        'phone': '02792 223 870',
    }
    manager_info = {
        'name': 'Mr. John Doe',
        'role': 'Manager',
        'photo': 'images/person_2.jpg',
        'email': 'manager@suryagardenhotel.com',
        'phone': '02792 223 871',
    }

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_obj = form.save(commit=False)
            contact_obj.user = request.user
            contact_obj.save()
            return redirect('index')
    else:
        form = ContactForm()

    all_messages = Contact.objects.all()
    return render(request, 'contact.html', {
        'form': form,
        'owner': owner_info,
        'manager': manager_info,
        'messages': all_messages,
    })

def gallary(request):
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'gallary.html', {'images': images})

# ----------------- RESERVATION -------------------

@login_required(login_url='login')
def reservation_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            reservation.room.status = "Booked"
            reservation.room.save()

            # ✅ Session store last reservation id
            request.session['last_reservation_id'] = reservation.id
            messages.success(request, "Reservation successfully created!")
            return redirect('reservation_display')
    else:
        form = ReservationForm()

    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservationform.html', {'form': form, 'reservations': reservations})

@login_required(login_url='login')
def reservation_list(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservation_display.html', {'reservations': reservations})

@login_required(login_url='login')
def cancel_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id, user=request.user)
    if request.method == 'POST':
        reservation.room.status = "Available"
        reservation.room.save()
        reservation.delete()
        messages.success(request, "Reservation cancelled successfully!")
    return redirect('reservation_display')

@login_required(login_url='login')
def update_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id, user=request.user)
    if request.method == 'POST':
        form = ReservationUpdateForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation updated successfully!")
            return redirect('reservation_display')
    else:
        form = ReservationUpdateForm(instance=reservation)
    return render(request, 'reservation_update.html', {'form': form})

def view_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'view_room.html', {'room': room})

# ----------------- AUTH -------------------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not email or not phone or not password or not password2:
            messages.error(request, "Please fill all fields.")
            return redirect('signup')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        messages.success(request, "User registered successfully. Please log in.")
        return redirect('login')

    return render(request, 'signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        # ✅ Admin login check
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            request.session['username'] = ADMIN_USERNAME
            request.session['last_login'] = str(request.session.get('_auth_user_id', 'admin'))
            return redirect('admin_dashboard')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['is_admin'] = False
            request.session['username'] = user.username
            request.session['last_login'] = str(user.last_login) if user.last_login else "First Login"
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)          # clear Django auth session
    request.session.flush()  # ✅ clear custom session data
    return redirect('index')

# ----------------- BOOKING + PAYMENT -------------------

@login_required(login_url='login')
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.room = room
            reservation.user = request.user
            reservation.save()

            # ✅ Update room status after booking
            room.status = "Booked"   # Available → Booked
            room.save()

            # ✅ Session store booking info
            request.session['last_reservation_id'] = reservation.id
            request.session['last_room'] = room.name

            return redirect('paypal_payment', reservation_id=reservation.id)
    else:
        form = ReservationForm()
    return render(request, 'book_room.html', {'form': form, 'room': room})


@login_required(login_url='login')
def paypal_payment(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    total_days = (reservation.check_out - reservation.check_in).days or 1
    total_price = reservation.room.price * total_days

    if request.method == 'POST':
        reservation.payment_done = True
        reservation.save()

        Payment.objects.create(
            reservation=reservation,
            amount=total_price,
            method='PayPal',
            success=True
        )

        # ✅ Session mark payment done
        request.session['last_payment'] = reservation.id

        return redirect('payment_success')

    return render(request, 'paypal_payment.html', {
        'reservation': reservation,
        'total_days': total_days,
        'total_price': total_price
    })

@login_required(login_url='login')
def payment_success(request):
    return render(request, 'payment_success.html')

@login_required(login_url='login')
def generate_bill(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if not reservation.payment_done:
        messages.warning(request, "Please complete payment first!")
        return redirect('paypal_payment', reservation_id=reservation.id)

    total_days = (reservation.check_out - reservation.check_in).days or 1
    total_price = reservation.room.price * total_days

    bill, created = Bill.objects.get_or_create(
        reservation=reservation,
        defaults={'total_price': total_price, 'paid': True}
    )

    # ✅ Session store bill info
    request.session['last_bill'] = bill.id
    return render(request, 'bill.html', {'reservation': reservation, 'total_price': total_price})

# ----------------- ADMIN -------------------

def admin_dashboard(request):
    if not request.session.get('is_admin'):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('index')

    total_customers = User.objects.count()
    total_rooms = Room.objects.count()
    total_bookings = Reservation.objects.count()
    total_feedbacks = Feedback.objects.count()
    total_payments = Payment.objects.count()

    context = {
        'total_customers': total_customers,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'total_feedbacks': total_feedbacks,
        'total_payments': total_payments,
    }
    return render(request, 'hotel_app/admin.html', context)

def admin_users(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'hotel_app/users.html', {'users': users})

def admin_bookings(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    reservations = Reservation.objects.all()
    return render(request, 'hotel_app/bookings.html', {'bookings': reservations})

def delete_booking(request, booking_id):
    if not request.session.get('is_admin'):
        return redirect('index')
    booking = get_object_or_404(Reservation, id=booking_id)
    booking.delete()
    return redirect('admin_bookings')

def admin_feedbacks(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    feedbacks = Feedback.objects.all()
    return render(request, 'hotel_app/feedbacks.html', {'feedbacks': feedbacks})

def admin_bills(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    bills = Bill.objects.all().order_by('-generated_at')
    return render(request, 'hotel_app/bills.html', {'bills': bills})

def delete_bill(request, bill_id):
    if not request.session.get('is_admin'):
        return redirect('index')
    bill = get_object_or_404(Bill, id=bill_id)
    bill.delete()
    messages.success(request, "Bill deleted successfully!")
    return redirect('admin_bills')

def admin_payments(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    payments = Payment.objects.all()
    return render(request, 'hotel_app/payments.html', {'payments': payments})

def admin_rooms(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    rooms = Room.objects.all()
    return render(request, 'hotel_app/rooms.html', {'rooms': rooms})

def add_room(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_rooms')
    else:
        form = RoomForm()
    return render(request, 'hotel_app/add_room.html', {'form': form})

def update_room(request, room_id):
    if not request.session.get('is_admin'):
        return redirect('index')
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('admin_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotel_app/update_room.html', {'form': form, 'room': room})

def delete_room(request, room_id):
    if not request.session.get('is_admin'):
        return redirect('index')
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('admin_rooms')

def delete_user(request, user_id):
    if not request.session.get('is_admin'):
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.warning(request, "You cannot delete yourself.")
    return redirect('users')

def admin_logout(request):
    if not request.session.get('is_admin'):
        return redirect('index')
    request.session.flush()   # ✅ Clear admin session
    return redirect('login')
