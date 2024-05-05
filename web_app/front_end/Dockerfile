FROM node:18-alpine

RUN npm install -g http-server

RUN mkdir /front_end
WORKDIR /front_end

COPY . .

RUN npm install

RUN npm run build

EXPOSE 3000
CMD [ "npm", "run", "serve", "--", "--port", "3000" ]