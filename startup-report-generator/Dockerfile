FROM python:3.11-slim

# Install system dependencies needed for weasyprint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libfontconfig1 \
    libcairo-gobject2 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the startup-report-generator directory contents
COPY startup-report-generator/requirements.txt .
COPY startup-report-generator/start.py .
COPY startup-report-generator/backend ./backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the web server startup script
CMD ["python", "start.py"] 