Reference Guide: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/

# check docker compose installation
docker compose version
# first go into the directory where you have created this docker-compose.yaml file
cd monitoring

# create the docker-compose.yaml file
touch docker-compose.yaml

# edit yaml file 
services:
  grafana:
    image: grafana/grafana-enterprise
    container_name: grafana
    restart: unless-stopped
    ports:
      - '3000:3000'
    volumes:
      - grafana-storage:/var/lib/grafana
# Use Docker volumes when you want the Docker Engine to manage the storage volume.
# To use Docker volumes for persistent storage,
volumes:
  grafana-storage: {}

# start/stop the grafana container
# d = detached mode
# up = to bring the container up and running
# To determine that Grafana is running, 
# open a browser window and type IP_ADDRESS:3000. The sign in screen should appear.
docker compose up -d
# down = to bring the container down and stopping
docker compose down
