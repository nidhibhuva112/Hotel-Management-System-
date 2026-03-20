from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Frontend pages
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('rooms/', views.rooms, name='rooms'),
    path('restaurant/', views.restaurant, name='restaurant'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('gallary/', views.gallary, name='gallary'),

    # Reservation
    path('reservation/', views.reservation_view, name='reservation'),
    path('reservation/list/', views.reservation_list, name='reservation_display'),
    path('reservation/cancel/<int:id>/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/update/<int:id>/', views.update_reservation, name='reservation_update'),
    path('view_room/<int:room_id>/', views.view_room, name='view_room'),
    path('book_room/<int:room_id>/', views.book_room, name='book_room'),

    # Payment
    path('paypal/payment/<int:reservation_id>/', views.paypal_payment, name='paypal_payment'),
    path('paypal/success/', views.payment_success, name='payment_success'),

    # Generate Bill
    path('generate-bill/<int:reservation_id>/', views.generate_bill, name='generate_bill'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/users/', views.admin_users, name='users'),
    path('dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('dashboard/bookings/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('dashboard/feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
    path('dashboard/payments/', views.admin_payments, name='admin_payments'),
    path('dashboard/rooms/', views.admin_rooms, name='admin_rooms'),
    path('dashboard/rooms/add/', views.add_room, name='add_room'),
    path('dashboard/rooms/update/<int:room_id>/', views.update_room, name='update_room'),
    path('dashboard/rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('dashboard/bills/', views.admin_bills, name='admin_bills'),
    path('dashboard/bills/delete/<int:bill_id>/', views.delete_bill, name='delete_bill'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
