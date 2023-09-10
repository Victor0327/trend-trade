FROM node:15.14.0-alpine as builder

WORKDIR /workspace

COPY package*.json ./

RUN node -v
RUN npm -v
RUN npm install --no-optional && npm cache clean --force

COPY . ./

RUN echo 'npm run start' > start.sh

CMD ["sh", "start.sh"]
