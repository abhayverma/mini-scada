FROM node:20-alpine

WORKDIR /app

# Install dependencies first for caching
COPY package.json ./
RUN npm install

# Copy the rest of the code
COPY . .

# Start the Vite development server
CMD ["npm", "run", "dev"]