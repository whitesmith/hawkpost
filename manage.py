#!/usr/bin/env python
import os
import sys
import dotenv

if __name__ == "__main__":
    dotenv.read_dotenv()
    environment = os.environ.get("HAWKPOST_ENV", "development")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "hawkpost.settings.{}".format(environment))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
