FROM node:18
EXPOSE 8080
WORKDIR /app
COPY vue/. .
RUN npm install
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
