USE academia360;

CREATE TABLE IF NOT EXISTS Tbl_AttendanceJustifications (
    JustificationID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ScheduleID INT NULL,
    JustificationDate DATE NOT NULL,
    Reason TEXT NOT NULL,
    Status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    DocumentPath VARCHAR(255),
    ReviewedByUserID INT NULL,
    ReviewedAt DATETIME NULL,

    InsertUsername VARCHAR(120) NOT NULL DEFAULT 'system',
    InsertDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangeUsername VARCHAR(120),
    ChangeDate DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (StudentID) REFERENCES Tbl_Students(StudentID),
    FOREIGN KEY (ScheduleID) REFERENCES Tbl_GeneratedSchedule(ScheduleID),
    FOREIGN KEY (ReviewedByUserID) REFERENCES Tbl_Users(UserID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
