import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
CREDENTIALS_REQUIRED = "Email and password are required."
INVALID_EMAIL = "Invalid email format."
EMAIL_ALREADY_IN_USE = "Email already in use."
USER_CREATED = "User created successfully."
INVALID_CREDENTIALS = "Invalid credentials."
SEARCH_QUERY_REQUIRED = "Search query is required."
RECIPIENT_ID_REQUIRED = "Recipient ID is required."
RECIPIENT_NOT_EXIST = "Recipient does not exist."
FRIEND_REQUEST_ALREADY_SENT = "Friend request already sent."
FRIEND_REQUEST_NOT_FOUND = "Friend request not found."
FRIEND_REQUEST_SENT = "Friend request sent."
FRIEND_REQUEST_ACCEPTED = "Friend request accepted."
FRIEND_REQUEST_REJECTED = "Friend request rejected."
REQUEST_ID_REQUIRED = "Request ID Required."
ACTION_AND_RECIPIENT_ID_REQUIRED = 'Action and recipient ID are required.'
INVALID_ACTION = 'Invalid action.'