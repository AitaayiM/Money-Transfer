from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination

from .filters import TransactionFilter
from .models import Transaction, Status
from .serializers import TransactionSerializer, CustomizedTransactionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .tasks import process_transaction_task
from identities.decorators import role_required
from identities.models import Roles, User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(Roles.RECEIVER)
def list_received_transactions(request):
    try:
        filterset = TransactionFilter(request.GET, queryset=Transaction.objects.filter(receiver=request.user), request=request)
        count = filterset.qs.count()
        res_page = 15
        paginator = PageNumberPagination()
        paginator.page_size = res_page

        queryset = paginator.paginate_queryset(filterset.qs, request)
        serializer = CustomizedTransactionSerializer(queryset, many=True)
        return Response({"users":serializer.data, "per page":res_page, "count":count})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.AGENT)
def process_transaction(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    if transaction.status != Status.PENDING:
        return Response({"error": "Transaction already processed"}, status=status.HTTP_400_BAD_REQUEST)

    # Assign the agent to the transaction
    transaction.agent = request.user

    action = request.data.get('action')
    if action == Status.CONFIRMED:
        transaction.status = Status.PROCESSED
        transaction.save()
        process_transaction_task.delay(transaction.id)  # Exécuter la tâche asynchrone
        return Response({"message": "Transaction is being processed"}, status=status.HTTP_200_OK)
    elif action == Status.CANCELLED:
        transaction.status = Status.CANCELLED
        transaction.save()
        return Response({"message": "Transaction cancelled"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(Roles.SENDER)
def create_transaction(request):
    data = request.data

    # Check if receiver is provided
    receiver_username = data.get('receiver')
    if not receiver_username:
        return Response({"error": "Receiver username must be provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Try to get the receiver
    try:
        receiver = User.objects.get(username=receiver_username)
    except User.DoesNotExist:
        return Response({"error": "The receiver does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Check that the receiver is not the sender
    if receiver == request.user:
        return Response({"error": "You cannot send money to yourself."}, status=status.HTTP_400_BAD_REQUEST)

    # Assign the receiver ID to the data
    data['receiver'] = receiver.id

    # Serialize the data
    serializer = TransactionSerializer(data=data)

    if serializer.is_valid():
        serializer.save(sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Return validation errors if the serializer is not valid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
