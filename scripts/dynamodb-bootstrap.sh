#!/bin/bash

aws dynamodb create-table --cli-input-json file://dynamodb-table.json --endpoint-url http://localhost:8000

