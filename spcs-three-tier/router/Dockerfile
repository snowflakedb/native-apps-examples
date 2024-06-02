FROM nginx:alpine
 
RUN apk update && apk add bash

EXPOSE 8000

COPY nginx.conf /nginx.conf

CMD ["/bin/sh" , "-c" , "envsubst '$FE_SERVER $BE_SERVER' < /nginx.conf > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"]
