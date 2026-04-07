FROM node:20-alpine

WORKDIR /app

# Install Chrome and Lighthouse
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-dejavu \
    && npm install -g lighthouse

# Create app directory
RUN mkdir -p /app/generated_sites

# Copy any initialization scripts
COPY . .

# Install dependencies (if any)
RUN npm install 2>/dev/null || true

EXPOSE 9000

CMD ["node", "server.js"]
