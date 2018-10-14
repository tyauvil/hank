# Hank
URL shortener written in Python (Flask)

### Why
This is a toy Flask app for me to learn how to write a Flask app that interacts with DynamoDB and Redis

### How

Environment variables:
```
REDIS_ENABLED     True||False
REDIS_HOST        localhost
PORT              5000
FLASK_URL         http://localhost:5000
DYNAMODB_ENDPOINT http://localhost:8000
SALT              random bytes to salt the hash function
CODED_OFFSET      Offset to begin in the hash/base58 output
CODED_LENGTH      Lenght of shortened URL (6)
```

### Who
Hank Pym is the alter ego of Ant-Man. His Pym particles make big things small.

![Ant-Man](images/antman.png)
