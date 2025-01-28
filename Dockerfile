# Use the official Nginx image
FROM nginx:alpine

# Copy the static website to the Nginx html folder
COPY index.html /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

