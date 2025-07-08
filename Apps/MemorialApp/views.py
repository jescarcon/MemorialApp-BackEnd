from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
import replicate
import requests
from django.core.files.base import ContentFile

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Medium, Note, User
from .serializers import MediumSerializer, NoteSerializer, UserSerializer


class MediumViewSet(viewsets.ModelViewSet):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer

    def perform_create(self, serializer):
        generate_ai = self.request.data.get('generate_ai_image', False)
        instance = serializer.save(user=self.request.user)

        if str(generate_ai).lower() == 'true':
            img_file = generar_imagen_con_replicate(instance.title)
            if img_file:
                instance.image.save(f"{instance.title}.png", img_file, save=True)

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Función interna para generar y enviar código 2FA
    def generate_and_send_2fa(self, user):
        code = f"{random.randint(100000, 999999)}"
        user.two_fa_code = code
        user.two_fa_expiration = timezone.now() + timedelta(minutes=5)
        user.save()

        send_mail(
            'Código de verificación 2FA',
            f'Tu código de verificación es: {code}',
            'no-reply@tuapp.com',
            [user.email],
        )

    # Acción para enviar código 2FA
    @action(detail=False, methods=['post'])
    def send_2fa_code(self, request):
        user = request.user
        self.generate_and_send_2fa(user)
        return Response({'detail': 'Código enviado'}, status=status.HTTP_200_OK)

    # Acción para verificar código 2FA
    @action(detail=False, methods=['post'])
    def verify_2fa_code(self, request):
        code = request.data.get('code')
        user = request.user

        if (user.two_fa_code == code and
            user.two_fa_expiration and
            timezone.now() < user.two_fa_expiration):
            user.two_fa_code = ''
            user.two_fa_expiration = None
            user.save()
            return Response({'detail': 'Código válido'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Código inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)


#region generar imagen con ia
import replicate
import requests
from django.core.files.base import ContentFile

REPLICATE_API_TOKEN = ""
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

def generar_imagen_con_replicate(titulo):
    prompt = f"Illustration of {titulo}, digital art"
    
    # Ejecuta un modelo público que genera imágenes, por ejemplo black-forest-labs/flux-schnell
    output = replicate_client.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": prompt}
    )
    
    # output es una lista de FileOutput (archivos)
    if output and len(output) > 0:
        image_url = output[0].url  # o output[0] directamente si es URL
        
        # Descarga la imagen
        response = requests.get(image_url)
        if response.status_code == 200:
            return ContentFile(response.content)
    
    return None

#endregion

