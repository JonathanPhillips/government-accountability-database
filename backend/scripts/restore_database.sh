#!/bin/bash
# Database Restore Script for Production
# This script restores PostgreSQL database from backup files

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo "Example: $0 /backups/gadb_backup_20260112_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Parse DATABASE_URL to extract connection details
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')

echo "WARNING: This will restore the database from backup and overwrite existing data!"
echo "Database: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "Starting database restore..."

# Create a backup of current database before restore
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP="/backups/pre_restore_backup_${TIMESTAMP}.sql.gz"
echo "Creating backup of current database: ${CURRENT_BACKUP}"

export PGPASSWORD="${DB_PASSWORD}"
pg_dump -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-acl \
        | gzip > "${CURRENT_BACKUP}"

echo "Current database backed up successfully"

# Restore from backup
echo "Restoring database from: ${BACKUP_FILE}"
gunzip -c "${BACKUP_FILE}" | psql -h "${DB_HOST}" \
                                   -p "${DB_PORT}" \
                                   -U "${DB_USER}" \
                                   -d "${DB_NAME}" \
                                   -q

echo "Database restored successfully from ${BACKUP_FILE}"
echo ""
echo "Note: A backup of the previous database state was saved to:"
echo "${CURRENT_BACKUP}"
