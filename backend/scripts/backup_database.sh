#!/bin/bash
# Database Backup Script for Production
# This script creates PostgreSQL database backups and optionally uploads to S3

set -e

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="gadb_backup_${TIMESTAMP}.sql.gz"

# Parse DATABASE_URL to extract connection details
# Format: postgresql://user:password@host:port/dbname
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)/\1/p')

echo "Starting database backup: ${BACKUP_FILE}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create backup
export PGPASSWORD="${DB_PASSWORD}"
pg_dump -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-acl \
        | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

echo "Backup created successfully: ${BACKUP_DIR}/${BACKUP_FILE}"

# Get backup file size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
echo "Backup size: ${BACKUP_SIZE}"

# Upload to S3 if configured
if [ ! -z "${S3_BACKUP_BUCKET}" ]; then
    echo "Uploading backup to S3: s3://${S3_BACKUP_BUCKET}/${BACKUP_FILE}"
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" \
        "s3://${S3_BACKUP_BUCKET}/${BACKUP_FILE}" \
        --storage-class STANDARD_IA
    echo "S3 upload completed"
fi

# Clean up old backups (keep last N days)
echo "Cleaning up backups older than ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -name "gadb_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List remaining backups
echo "Remaining backups:"
ls -lh "${BACKUP_DIR}"/gadb_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "Backup process completed successfully"
