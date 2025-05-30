# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all files (including config.json)
COPY . .

# Make sure config.json is in the right location
# If your config.json is in a specific location, copy it there
COPY config.json /Users/ericasmith/not_icloud/survey-project-20250419/

# Install Python packages your app needs
RUN pip install flask anthropic

# Expose the port your app runs on (adjust if different)
EXPOSE 5000

# Set working directory for the app
WORKDIR /app/frontend/project-directory

# Create a simple startup script
RUN echo 'import app; app.app.run(host="0.0.0.0", port=5000, debug=True)' > start_app.py

# Run the startup script
CMD ["python", "start_app.py"]