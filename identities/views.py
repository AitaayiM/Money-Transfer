import random
import string
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.test import APIRequestFactory

from .decorators import role_required
from .filters import UserFilter
from .models import User, Role, Roles, Profile
from .serializers import SignUpSerializer
from .tasks import (
    send_verification_email, send_reset_password_email,
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.AGENT)
def get_all_users(request):
    try:
        filterset = UserFilter(request.GET, queryset=User.objects.all(), request=request)
        count = filterset.qs.count()
        res_page = 15
        paginator = PageNumberPagination()
        paginator.page_size = res_page

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = SignUpSerializer(queryset, many=True)
        return Response({"users":serializer.data, "per page":res_page, "count":count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    user = SignUpSerializer(data = data)

    if user.is_valid():
        if not User.objects.filter(username = data['username']).exists():
            user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                username = data['username'],
                date_of_birth = data['date_of_birth'],
                gender = data['gender'],
                password = make_password(data['password']),
            )
            receiver_role, created = Role.objects.get_or_create(name=Roles.RECEIVER)
            sender_role, created = Role.objects.get_or_create(name=Roles.SENDER)
            user.roles.add(receiver_role)
            user.roles.add(sender_role)
            return Response(
                {'details':'Your account registered successfully!'},
                status= status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error':'Email or password invalid!'},
                status= status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(user.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        profile = Profile.objects.get(user_id=user.id)
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        profile.one_time_password = verification_code
        profile.one_time_password_expire = timezone.now() + timedelta(hours=1)
        profile.save()


        send_verification_email.delay(email, verification_code)
        return Response({'detail': 'Verification code sent successfully.'}, status=status.HTTP_200_OK)

    return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_verification(request):
    email = request.data.get('email')
    password = request.data.get('password')
    one_time_password = request.data.get('one_time_password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        user_profile = Profile.objects.get(user=user)
        # Check if the verification code is valid and not expired
        if (
            user_profile.one_time_password is not None and
            user_profile.one_time_password == one_time_password and
            user_profile.one_time_password_expire > timezone.now()
        ):
            # Verification successful, generate access and refresh tokens
            django_login(request, user)
            # Verification successful, generate access and refresh tokens
            factory = APIRequestFactory()
            token_request = factory.post('/token/', {'username': email, 'password': password} ,format='json')
            token_obtain_pair_view = TokenObtainPairView.as_view()
            response = token_obtain_pair_view(token_request)
            # Reset verification code and expiry time
            user_profile.one_time_password = ''
            user_profile.one_time_password_expire = None
            user_profile.save()
            return response
    return Response({'detail': 'Invalid verification code or credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, username=data['email'])
    user = User.objects.get(id=user.id)
    token = get_random_string(40)
    expire_date = datetime.now() + timedelta(minutes=30)
    user.profile.one_time_password = token
    user.profile.one_time_password_expire = expire_date
    user.profile.save()
    link = "{host}api/reset_password/{token}/".format(host=get_current_host(request), token=token)
    send_reset_password_email.delay(data['email'], link)

    return Response({'details': 'Password reset sent to {email}'.format(email=data['email'])})


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__one_time_password=token)

    if user.profile.one_time_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'}, status.HTTP_400_BAD_REQUEST)

    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Password are not same'}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(data['password'])
    user.profile.one_time_password = ""
    user.profile.one_time_password_expire = None
    user.profile.save()
    user.save()
    return Response({'details': 'Password reset done'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.SENDER, Roles.RECEIVER)
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"details": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
