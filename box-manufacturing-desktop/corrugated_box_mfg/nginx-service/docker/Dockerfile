FROM nginx:alpine

COPY ../config/nginx.conf /etc/nginx/nginx.conf
COPY ../config/sites-available/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]