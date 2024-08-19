# person_detect

### 1) Fill the .env file with actual values, such as usernames, passwords


### 2) Download and install Docker:

[Official website](https://www.docker.com/)

### 3) Run and stop PostgreSQL to create DB for project:

```shell
docker run -d -e POSTGRES_DB=face_detect_db -e POSTGRES_PASSWORD=admin -e POSTGRES_USER=admin -v detect-db--volume:/var/lib/postgresql/data -p 5432:5432 --name face_detect_db postgres:13
docker stop face_detect_db
```

### 4) Build docker-compose:

```shell
docker-compose build
```

### 5) Up docker-compose:

```shell
docker-compose up
```
