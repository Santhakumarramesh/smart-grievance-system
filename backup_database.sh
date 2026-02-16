#!/bin/bash

# Smart Grievance System - Database Backup Script
# Run this script daily via cron: 0 2 * * * /path/to/backup_database.sh

BACKUP_DIR="backups"
DB_FILE="backend/grievance_system.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/grievance_system_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create backup
if [ -f "${DB_FILE}" ]; then
    cp ${DB_FILE} ${BACKUP_FILE}
    echo "✅ Backup created: ${BACKUP_FILE}"
    
    # Compress backup
    gzip ${BACKUP_FILE}
    echo "✅ Backup compressed: ${BACKUP_FILE}.gz"
    
    # Keep only last 30 days of backups
    find ${BACKUP_DIR} -name "*.db.gz" -mtime +30 -delete
    echo "✅ Old backups cleaned up (kept last 30 days)"
    
    # Log backup
    echo "$(date): Backup successful - ${BACKUP_FILE}.gz" >> ${BACKUP_DIR}/backup.log
else
    echo "❌ Error: Database file not found: ${DB_FILE}"
    echo "$(date): Backup failed - DB file not found" >> ${BACKUP_DIR}/backup.log
    exit 1
fi
