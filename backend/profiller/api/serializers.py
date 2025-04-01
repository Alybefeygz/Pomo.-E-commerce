from profiller.models import Profil, ProfilDurum
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class ProfilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)
    foto = serializers.ImageField(read_only = True)
    
    # User modelinden alanları al
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    
    class Meta:
        model = Profil
        fields = ['id', 'user', 'foto', 'bio', 'email', 'first_name', 'last_name']
    
    def update(self, instance, validated_data):
        # User modeline ait değerleri al
        user_data = validated_data.pop('user', {})
        
        # Profil modelini güncelle
        instance = super().update(instance, validated_data)
        
        # User modelini güncelle
        if user_data:
            user = instance.user
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.last_name = user_data['last_name']
            user.save()
        
        return instance
        
        
class ProfilFotoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profil
        fields = ['foto']
        
        
class ProfilDurumSerializer(serializers.ModelSerializer):
    user_profil = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = ProfilDurum
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı bilgilerini serileştirmek için serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        # Password hash'ini döndürmek güvenli olmadığı için password'ü eklemedik

class CustomTokenSerializer(serializers.ModelSerializer):
    """Token ve kullanıcı bilgilerini birlikte döndüren serializer"""
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Token
        fields = ['key', 'user']
        
    def get_user(self, obj):
        """Token sahibi olan kullanıcının detaylarını döndürür"""
        user_data = UserSerializer(obj.user).data
        
        # Profil bilgilerini ekle
        try:
            profil = Profil.objects.get(user=obj.user)
            profil_data = ProfilSerializer(profil).data
            
            # Kullanıcı verilerine profil bilgilerini ekle
            user_data['foto'] = profil_data.get('foto', None)
            user_data['bio'] = profil_data.get('bio', None)
        except Profil.DoesNotExist:
            # Profil yoksa varsayılan değerler
            user_data['foto'] = None
            user_data['bio'] = None
        
        return user_data