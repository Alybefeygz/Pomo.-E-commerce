from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.authtoken.models import Token
import traceback

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST'])
def registration_view(request):
    logger.info('=== Registration Request Received ===')
    logger.info(f'Request Method: {request.method}')
    logger.info(f'Request Headers: {dict(request.headers)}')
    logger.info(f'Request Data: {request.data}')
    logger.info(f'Request Content Type: {request.content_type}')
    logger.info(f'Request User: {request.user}')
    
    try:
        # Registration logic will be handled by dj-rest-auth
        logger.info('Processing registration request...')
        
        # Validate required fields
        required_fields = ['username', 'email', 'password1', 'password2']
        missing_fields = [field for field in required_fields if field not in request.data]
        
        if missing_fields:
            logger.error(f'Missing required fields: {missing_fields}')
            return Response(
                {"detail": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email format
        try:
            validate_email(request.data.get('email'))
        except ValidationError:
            logger.error('Invalid email format')
            return Response(
                {"email": "Geçerli bir email adresi giriniz."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate username
        username = request.data.get('username', '')
        if len(username) < 3:
            logger.error('Username too short')
            return Response(
                {"username": "Kullanıcı adı en az 3 karakter olmalıdır."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            logger.error('Username already exists')
            return Response(
                {"username": "Bu kullanıcı adı zaten kullanılıyor."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email exists
        if User.objects.filter(email=request.data.get('email')).exists():
            logger.error('Email already exists')
            return Response(
                {"email": "Bu email adresi zaten kullanılıyor."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate passwords
        password1 = request.data.get('password1', '')
        password2 = request.data.get('password2', '')
        
        if len(password1) < 6:
            logger.error('Password too short')
            return Response(
                {"password1": "Şifre en az 6 karakter olmalıdır."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if password1 != password2:
            logger.error('Passwords do not match')
            return Response(
                {"password2": "Şifreler eşleşmiyor."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registration successful
        logger.info('Registration successful')
        return Response(
            {"detail": "Registration successful"},
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error('=== Registration Error ===')
        logger.error(f'Error Type: {type(e).__name__}')
        logger.error(f'Error Message: {str(e)}')
        logger.error(f'Request Data: {request.data}')
        logger.error(f'Request Headers: {dict(request.headers)}')
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def google_auth_view(request):
    try:
        logger.info('=== Google Auth Request Received ===')
        logger.info('Request data:', request.data)
        
        email = request.data.get('email')
        username = request.data.get('username')
        photo_url = request.data.get('photo_url')
        google_id = request.data.get('google_id')

        logger.info('Extracted data:', {
            'email': email,
            'username': username,
            'photo_url': photo_url,
            'google_id': google_id
        })

        if not email:
            logger.error('Email is missing')
            return Response(
                {"email": "Email adresi gereklidir."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Kullanıcıyı email'e göre bul veya oluştur
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'is_active': True
            }
        )

        logger.info(f'User {"created" if created else "found"}: {user.username}')

        # Eğer kullanıcı yeni oluşturulduysa
        if created:
            # Profil fotoğrafını güncelle
            if photo_url:
                user.profil.foto = photo_url
                user.profil.save()
                logger.info('Profile photo updated')

        # Token oluştur veya mevcut token'ı al
        token, _ = Token.objects.get_or_create(user=user)
        logger.info('Token created/retrieved successfully')

        response_data = {
            'key': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }
        
        logger.info('Sending response:', response_data)
        return Response(response_data)

    except Exception as e:
        logger.error('Google authentication error:', str(e))
        logger.error('Error details:', {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc()
        })
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        ) 