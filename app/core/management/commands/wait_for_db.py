"""
Django command to wait for db to be available
"""
from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError  # when the database is not ready


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Enterpoint for command"""
        self.stdout.write("... Waiting for database ...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2OpError, OperationalError):
                self.stdout.write('UNAVAILABLE DATABASE: \
                                  Database is not available at the moment...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('DATABASE AVAILABLE!'))
