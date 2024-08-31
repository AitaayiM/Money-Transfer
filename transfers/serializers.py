from rest_framework import serializers
from .models import Transaction, Status


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'agent', 'amount', 'status', 'created_at', 'updated_at']

    def validate_amount(self, value):
        """Vérifie que le montant est supérieur à 0."""
        if value <=0 :
            raise serializers.ValidationError("the amount must be greater than 0.")
        return value

    def validate(self, data):
        if data.get('status') == Status.CONFIRMED and not data.get('agent'):
            raise serializers.ValidationError("A transaction cannot be confirmed without an agent assigned.")
        return data


class CustomizedTransactionSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(method_name='get_sender_full_name', read_only=True)
    agent = serializers.SerializerMethodField(method_name='get_agent_full_name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'agent', 'amount', 'created_at']

    def validate_amount(self, value):
        """Vérifie que le montant est supérieur à 0."""
        if value <=0 :
            raise serializers.ValidationError("the amount must be greater than 0.")
        return value

    def validate(self, data):
        if data.get('status') == Status.CONFIRMED and not data.get('agent'):
            raise serializers.ValidationError("A transaction cannot be confirmed without an agent assigned.")
        return data

    def get_sender_full_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def get_agent_full_name(self, obj):
        return f"{obj.agent.first_name} {obj.agent.last_name}"

