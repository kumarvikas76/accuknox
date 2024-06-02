from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, FriendRequest
from .serializers import UserSerializer
from .pagination import SearchPagination
from . import constants,helpers
from .serializers import SignupSerializer, LoginSerializer
from django.db.models import Q

@api_view(['POST'])
def signup(request):
    """
    Handle user signup.

    This view accepts POST requests with 'email', 'password', and optionally 'name'.
    It validates the data, creates a new user, and returns a success message.
    """
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': constants.USER_CREATED}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """
    Handle user login.

    This view accepts POST requests with 'email' and 'password'.
    It validates the credentials, authenticates the user, and returns JWT tokens if successful.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': constants.INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """
    Search for users by email or name.

    This view accepts GET requests with a 'query' parameter.
    It searches for users whose email or name matches the query and returns a paginated response.
    """
    search_query = request.query_params.get('query', '')

    if not search_query:
        return Response({'error': constants.SEARCH_QUERY_REQUIRED}, status=status.HTTP_400_BAD_REQUEST)

    # Search users by email or name
    users_by_email = CustomUser.objects.filter(email__iexact=search_query)
    users_by_name = CustomUser.objects.filter(name__icontains=search_query)

    # Combine the querysets and remove duplicates
    all_users = (users_by_email | users_by_name).distinct()

    # Paginate the results
    paginator = SearchPagination()
    paginated_users = paginator.paginate_queryset(all_users, request)

    # Serialize the user data
    serializer = UserSerializer(paginated_users, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def friend_request(request):
    """
    Handle friend requests.

    This view accepts POST requests with 'action' (send, accept, reject) and 'recipient_id'.
    It handles sending, accepting, and rejecting friend requests.
    """
    action = request.data.get('action')
    recipient_id = request.data.get('recipient_id')

    if not action or not recipient_id:
        return Response({'error': constants.ACTION_AND_RECIPIENT_ID_REQUIRED}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the recipient user
        recipient = CustomUser.objects.get(id=recipient_id)
    except CustomUser.DoesNotExist:
        return Response({'error': constants.RECIPIENT_NOT_EXIST}, status=status.HTTP_404_NOT_FOUND)

    sender = request.user
    if action == 'send':
        # Throttle friend requests to prevent abuse
        throttle_instance = helpers.SendFriendRequestThrottle()
        if not throttle_instance.allow_request(request, view=None):
            return Response({'error': 'Request limit exceeded'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if FriendRequest.objects.filter(sender=sender, recipient=recipient).exists():
            return Response({'error': constants.FRIEND_REQUEST_ALREADY_SENT}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the friend request
        friend_request = FriendRequest(sender=sender, recipient=recipient)
        try:
            friend_request.save()
        except ValidationError as e:
            raise DRFValidationError(e.messages)
        return Response({'message': constants.FRIEND_REQUEST_SENT}, status=status.HTTP_201_CREATED)

    elif action == 'accept':
        try:
            # Retrieve the friend request to accept
            friend_request = FriendRequest.objects.get(sender=recipient, recipient=sender, status=FriendRequest.PENDING)
        except FriendRequest.DoesNotExist:
            return Response({'error': constants.FRIEND_REQUEST_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        # Accept the friend request
        friend_request.status = FriendRequest.ACCEPTED
        friend_request.save()
        return Response({'message': constants.FRIEND_REQUEST_ACCEPTED}, status=status.HTTP_200_OK)

    elif action == 'reject':
        try:
            # Retrieve the friend request to reject
            friend_request = FriendRequest.objects.get(sender=recipient, recipient=sender, status=FriendRequest.PENDING)
        except FriendRequest.DoesNotExist:
            return Response({'error': constants.FRIEND_REQUEST_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        # Reject the friend request
        friend_request.status = FriendRequest.REJECTED
        friend_request.save()
        return Response({'message': constants.FRIEND_REQUEST_REJECTED}, status=status.HTTP_200_OK)

    else:
        return Response({'error': constants.INVALID_ACTION}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """
    List the authenticated user's friends.

    This view accepts GET requests and returns a list of the user's friends.
    """
    user = request.user
    # Retrieve accepted friend requests involving the user
    accepted_friend_requests = FriendRequest.objects.filter(
        Q(sender=user) | Q(recipient=user),
        status=FriendRequest.ACCEPTED
    ).select_related('sender', 'recipient')

    # Extract friends from the friend requests
    friends = [
        friend_request.recipient if friend_request.sender == user else friend_request.sender
        for friend_request in accepted_friend_requests
    ]

    # Serialize the friend data
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_friend_requests(request):
    """
    List pending friend requests for the authenticated user.

    This view accepts GET requests and returns a list of users who have sent friend requests to the user.
    """
    user = request.user
    # Retrieve pending friend requests where the user is the recipient
    pending_friend_requests = FriendRequest.objects.filter(
        recipient=user,
        status=FriendRequest.PENDING
    ).select_related('sender')

    # Extract senders from friend requests
    senders = [friend_request.sender for friend_request in pending_friend_requests]

    # Serialize the sender data
    serializer = UserSerializer(senders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)







