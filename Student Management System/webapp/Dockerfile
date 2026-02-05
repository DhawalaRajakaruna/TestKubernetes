#Use an official Python runtime as a parent image
FROM python:3.12-slim

#Set the working Directory
WORKDIR /app

#Copy the current directory contents into the container at /app
# from all files in the current directory to /app in the container
COPY requirements.txt . 

#install all the dependancies 
RUN pip install --no-cache-dir -r requirements.txt

#Copy the rest of the application code to the container
COPY . .

#Make port 8000 available to the world outside this container
EXPOSE 8000

#Define environment variable
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]