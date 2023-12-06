
# FileUploadForm constants
SELECT_FILE_LABEL = 'Select an Excel file'
ALLOWED_FILE_FORMAT = 'Only Excel files are allowed.'
EXCEL_FORMAT_ERROR = 'File must be in Excel format (XLSX or XLS)'

# UserRegistrationForm and UserLoginForm constants
EMAIL_PLACEHOLDER = 'Enter your email'
USERNAME_PLACEHOLDER = 'Enter your username'
PASSWORD_PLACEHOLDER = 'Enter your password'
CONFIRM_PASSWORD_PLACEHOLDER = 'Confirm your password'
FIRST_NAME_PLACEHOLDER = 'Enter your first name'
LAST_NAME_PLACEHOLDER = 'Enter your last name'
CONTACT_PLACEHOLDER = 'Enter your contact number'
USERNAME_LABEL = 'Username'
PASSWORD_LABEL = 'Password'

# User model constants
USER_FIELDS = ['email', 'first_name', 'last_name', 'contact']
USER_GROUPS_RELATED_NAME = 'quizwise_user_groups'
USER_PERMISSIONS_RELATED_NAME = 'quizwise_user_permissions'

# PasswordReset model constants
OTP_LENGTH = 6

# Help texts for User model fields
EMAIL_HELP_TEXT = 'Please provide a valid email address.'
USERNAME_HELP_TEXT = 'Please choose a unique username.'
FIRST_NAME_HELP_TEXT = 'Enter your first name.'
LAST_NAME_HELP_TEXT = 'Enter your last name.'
CONTACT_HELP_TEXT = 'Enter a 10-digit contact number.'
GROUPS_HELP_TEXT = 'The groups this user belongs to. A user will get all permissions granted to each of their groups.'
USER_PERMISSIONS_HELP_TEXT = 'Specific permissions for this user.'

# Value errors for User model
EMAIL_VALUE_ERROR = 'Email is required'
USERNAME_VALUE_ERROR = 'Username is required'
CONTACT_VALUE_ERROR = 'Contact number must be 10 digits.'
