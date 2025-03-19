import os
from django.http import HttpResponse
# from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Restrict access to superusers only
# @user_passes_test(lambda u: u.is_superuser)
def download_database(request):
    try:
        # Assuming you're using SQLite; get the database file path
        db_path = settings.DATABASES['default']['NAME']
        
        # Check if the database file exists
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at {db_path}")
            return HttpResponse("Database file not found.", status=404)

        # Read the database file
        with open(db_path, 'rb') as db_file:
            db_data = db_file.read()

        # Create a response with the database file as a download
        response = HttpResponse(db_data, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="db.sqlite3"'
        response['Content-Length'] = len(db_data)

        logger.info("Database downloaded successfully by user: %s", request.user)
        return response

    except Exception as e:
        logger.error("Error downloading database: %s", str(e))
        return HttpResponse(f"Error downloading database: {str(e)}", status=500)