# ============================================================
# frontend/Dockerfile
# Multi-stage build for React (Vite) frontend
# ============================================================

# ----------------------------------------------------------
# Stage 1: Build the React application
# ----------------------------------------------------------
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# ----------------------------------------------------------
# Stage 2: Production nginx server
# ----------------------------------------------------------
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
