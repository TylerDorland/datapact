# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build args for API URLs
ARG VITE_API_BASE_URL=http://localhost:8001
ARG VITE_DICTIONARY_API_URL=http://localhost:8002
ARG VITE_NOTIFICATION_API_URL=http://localhost:8003

# Set as env vars for the build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_DICTIONARY_API_URL=$VITE_DICTIONARY_API_URL
ENV VITE_NOTIFICATION_API_URL=$VITE_NOTIFICATION_API_URL

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy production nginx config (no proxy, just static files)
COPY nginx.prod.conf /etc/nginx/nginx.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
