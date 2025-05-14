-- Increase logging level for debugging authentication
PRAGMA writable_schema = 1;
UPDATE sqlite_master SET sql = replace(sql, 'level=logging.INFO', 'level=logging.DEBUG') WHERE type='table' AND name='sqlite_master';
PRAGMA writable_schema = 0;