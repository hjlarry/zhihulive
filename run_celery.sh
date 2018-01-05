#!/bin/sh

su -m celery_user -c "celery worker -A app.tasks -l info"