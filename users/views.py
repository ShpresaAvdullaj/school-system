from rest_framework.decorators import api_view, permission_classes
from users.serializers import RegistrationSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdminOrReadOnly


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token_r = RefreshToken(refresh_token)
            token_r.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"], )
@permission_classes((IsAdminOrReadOnly, ))
def registration_view(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data["response"] = "Registration successful!"
            data["username"] = account.username
            data["email"] = account.email
            data["role"] = account.role
            refresh = RefreshToken.for_user(account)
            data["token"] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            data = serializer.errors
        return Response(data, status=status.HTTP_201_CREATED)
