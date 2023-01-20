from rest_framework import serializers
from users.models import CustomUser

ROLE = (
    ("ADMIN", "Admin"),
    ("STUDENT", "student"),
    ("TEACHER", "teacher"),
)


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    role = serializers.ChoiceField(choices=ROLE)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "password2", "role"]

    def save(self):

        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"error": "P1 and P2 should be same!"})

        if CustomUser.objects.filter(email=self.validated_data["email"]).exists():
            raise serializers.ValidationError({"error": "Email already exists!"})

        account = CustomUser(email=self.validated_data["email"],
                             username=self.validated_data["username"],
                             role=self.validated_data["role"])
        account.set_password(password)
        account.save()

        return account
