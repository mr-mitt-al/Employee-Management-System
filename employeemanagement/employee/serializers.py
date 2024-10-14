from rest_framework import serializers
from .models import Employee, RequestLeave
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name',  'age', 'phone_number', 'position',
            'description', 'hiring_date', 'profile_picture', 'email']
        read_only_fields = ['id', 'hiring_date',]

    def create(self, validated_data):
        """
        Overriding the default create method to handle password hashing
        """
        user = Employee(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            phone_number=validated_data.get('phone_number', ''),
            position=validated_data['position'],
            description=validated_data.get('description', ''),
            profile_picture=validated_data.get('profile_picture', None)
        )
        password = validated_data.pop('password', None)
        if password:
            user.set_password(password)
            # Hashing the user password
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Overriding the update method to handle password updates and user data updates.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        # instance.email = validated_data.get('email', instance.email)
        instance.age = validated_data.get('age', instance.age)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.position = validated_data.get('position', instance.position)
        instance.description = validated_data.get('description', instance.description)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Checking if new_password and confirm_password are same or not
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and Confirm password do not match.")
        if len(data['new_password']) < 8:
            # new password length should be greater than 7 characters
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return data

    def validate_old_password(self, value):
        # Checking if old password is correct or not
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class RequestLeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = RequestLeave
        fields = ['id', 'employee', 'employee_name', 'reason', 'start_date', 'end_date', 'leave_status', 'leave_requested_at']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"