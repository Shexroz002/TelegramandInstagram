# Use an official Python runtime as a parent image
FROM python:3.8
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Set the working directory to /my_future
WORKDIR /my_future

# Copy the current directory contents into the container at /my_future
COPY . /my_future

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Celery
ENV C_FORCE_ROOT true

# CMD ["python", "manage.py", "runserver"]
# Use gunicorn to run your application, this is a more production-ready setup
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "my_future.wsgi:application"]
