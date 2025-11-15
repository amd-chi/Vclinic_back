#!/bin/bash

# بررسی اینکه نام سرویس ورودی داده شده است یا خیر
if [ -z "$1" ]; then
    echo "Usage: source ./set_env.sh <name>"
    return 1
fi

SERVICE_NAME=$1

# بررسی اینکه فایل .env.{name} وجود دارد یا خیر
ENV_FILE=".env.${SERVICE_NAME}"
if [ ! -f "$ENV_FILE" ]; then
    echo "Environment file $ENV_FILE not found!"
    return 1
fi

# بارگذاری متغیرهای محیطی از فایل .env.{name}
export $(grep -v '^#' "$ENV_FILE" | xargs)

echo "Environment variables from $ENV_FILE loaded successfully."
