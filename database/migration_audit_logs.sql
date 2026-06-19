CREATE TABLE IF NOT EXISTS Tbl_AuditLogs (
    AuditLogID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NULL,
    UserEmail VARCHAR(255) NULL,
    UserRole VARCHAR(80) NULL,
    Action VARCHAR(80) NOT NULL,
    Module VARCHAR(80) NOT NULL,
    EntityType VARCHAR(120) NULL,
    EntityID VARCHAR(80) NULL,
    Summary VARCHAR(255) NOT NULL,
    Details JSON NULL,
    IpAddress VARCHAR(64) NULL,
    UserAgent VARCHAR(255) NULL,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_audit_user (UserID),
    INDEX idx_audit_action (Action),
    INDEX idx_audit_module (Module),
    INDEX idx_audit_entity (EntityType, EntityID),
    INDEX idx_audit_created_at (CreatedAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
