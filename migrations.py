from peewee import *
from playhouse.migrate import *
from model import db

migrator = SqliteMigrator(db)

has_had_reminder = BooleanField(default=False, null=False)

migrate(
    migrator.add_column('volunteershiftrelation', 'has_had_reminder', has_had_reminder)
)
