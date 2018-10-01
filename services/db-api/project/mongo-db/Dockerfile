FROM mongo:latest

# add entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

#CMD ["mongo admin","db.createUser({user: '[username]', pwd: '[password]', roles:[{role:'root',db:'admin'}]});"]

# run server
CMD ["/usr/src/app/entrypoint.sh"]