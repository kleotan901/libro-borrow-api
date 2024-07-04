# LibroBorrow API


Developed the LibroBorrow API, a comprehensive online library service that streamlines the borrowing and returning of books for users.
### Key Features:

* JWT Authentication: Secure user authentication and authorization.
* Admin Panel: Accessible at /admin/ for managing library resources and user activities.
* API Documentation: Detailed documentation available at /api/doc/swagger/.
* Borrowing Management: Enabled users to create and manage borrowings, including returning books via endpoints (e.g., /api/borrowings/1/return/).
* Book Inventory: Displayed the number of available books and their daily fee.
* Filtering Capabilities: Allowed filtering of borrowings by user and active status.
* Administrator Features: Enabled book creation with administrator rights.
* Telegram Bot Integration: Provided real-time updates and information on borrowings via a Telegram bot.
* Notifications: Implemented daily notifications for overdue borrowings and alerts for new borrowings.

## Run project without docker
+ git clone https://github.com/kleotan901/libro-borrow-api.git
+ cd libro-borrow-api
+ python -m venv venv
+ venv\Scripts\activate (on Windows)
+ source venv/bin/activate (on macOS)
+ pip install -r requirements.txt
+ python manage.py migrate
+ python manage.py runserver
+ python manage.py loaddata library_service_project_fixture.json
+ celery -A library-service-project beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
+ celery -A library-service-project worker -l INFO #run celery worker for task handling
+ python telegram_notifications/notifications.py #run telegram for telegram notifications

## Run with docker
Docker should be installed
+ git clone https://github.com/kleotan901/libro-borrow-api.git
+ cd library-service-project
+ docker-compose up --build

## Getting access

+ create new user via /api/user/register/
+ get access token via /api/user/token/
+ get link to start telegram bot /api/telegram_notifications/start/

### You can use the following test credentials:

##### Test superuser:
- Email: admin@admin.com
- Password: qay12345


## Configuration
The project uses environment variables for configuration. Please follow these steps to set up the required configuration files.

The .env file is used to store sensitive information and configuration variables that are necessary for the project to function properly.

The .env.sample file serves as a template or example for the .env file. It includes the necessary variables and their expected format, but with placeholder values.
 
 To configure the project:

- Locate the .env.sample file in the project's root directory.
- Duplicate the .env.sample file and rename the duplicated file to .env.
- Open the .env file and replace the placeholder values with the actual configuration values specific to your setup.

Remember to keep the .env file secure and avoid sharing it publicly or committing it to version control systems.
