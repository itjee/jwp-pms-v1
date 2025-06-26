"""
Application Constants

All constant values used throughout the application.

클래스 기반 상수 사용의 장점:

1. 간단함: Python Enum보다 단순하고 직관적
2. 유연성: 클래스 메서드로 다양한 유틸리티 함수 추가 가능
3. 가독성: IDE에서 자동완성 지원하며 더 명확한 구조
4. 검증: is_valid() 메서드로 값 유효성 검증 가능
5. 선택지: choices() 메서드로 폼이나 API에서 사용할 수 있는 선택지 제공
6. 데이터베이스: SQLAlchemy에서 String 타입으로 간단하게 사용 가능

사용 예시:

# 1. 기본 사용
user.role = UserRole.ADMIN
project.status = ProjectStatus.ACTIVE

# 2. 검증
if UserRole.is_valid(user_input):
    user.role = user_input

# 3. 선택지 생성 (API나 폼에서 사용)
role_choices = UserRole.choices()
# [('admin', 'Admin'), ('manager', 'Manager'), ...]

# 4. 필터링
admin_users = User.query.filter(User.role == UserRole.ADMIN).all()

# 5. 조건부 로직
if user.role in [UserRole.ADMIN, UserRole.MANAGER]:
    # 관리자 로직
    pass

# 6. 동적 값 체크
all_roles = UserRole.values()
for role in all_roles:
    print(f"Role: {role}")
"""

# =============================================================================
# User Related Constants
# =============================================================================


class UserRole:
    """User role constants"""

    ADMIN = "admin"  # Administrator with full access
    MANAGER = "manager"  # Project or team manager with elevated permissions
    DEVELOPER = "developer"  # Developer with standard permissions
    TESTER = "tester"  # Tester with permissions to test and report issues
    GUEST = "guest"  # Guest user with limited access
    CONTRIBUTOR = "contributor"  # User who can contribute content
    VIEWER = "viewer"  # User who can only view content without making changes

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.ADMIN, "Admin"),
            (cls.MANAGER, "Manager"),
            (cls.DEVELOPER, "Developer"),
            (cls.TESTER, "Tester"),
            (cls.GUEST, "Guest"),
            (cls.CONTRIBUTOR, "Contributor"),
            (cls.VIEWER, "Viewer"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.ADMIN,
            cls.MANAGER,
            cls.DEVELOPER,
            cls.TESTER,
            cls.GUEST,
            cls.CONTRIBUTOR,
            cls.VIEWER,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class UserStatus:
    """User status constants"""

    ACTIVE = "active"  # Active user account
    INACTIVE = "inactive"  # Inactive user account
    SUSPENDED = "suspended"  # Suspended user account
    PENDING = "pending"  # User account pending activation or approval

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.ACTIVE, "Active"),
            (cls.INACTIVE, "Inactive"),
            (cls.SUSPENDED, "Suspended"),
            (cls.PENDING, "Pending"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.ACTIVE, cls.INACTIVE, cls.SUSPENDED, cls.PENDING]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# Project Related Constants
# =============================================================================


class ProjectStatus:
    """Project status constants"""

    PLANNING = "planning"  # Project in planning phase
    ACTIVE = "active"  # Active project
    ON_HOLD = "on_hold"  # Project temporarily on hold
    COMPLETED = "completed"  # Successfully completed project
    CANCELLED = "cancelled"  # Cancelled project
    ARCHIVED = "archived"  # Archived project

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.PLANNING, "Planning"),
            (cls.ACTIVE, "Active"),
            (cls.ON_HOLD, "On Hold"),
            (cls.COMPLETED, "Completed"),
            (cls.CANCELLED, "Cancelled"),
            (cls.ARCHIVED, "Archived"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.PLANNING,
            cls.ACTIVE,
            cls.ON_HOLD,
            cls.COMPLETED,
            cls.CANCELLED,
            cls.ARCHIVED,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class ProjectPriority:
    """Project priority constants"""

    LOW = "low"  # Low priority
    MEDIUM = "medium"  # Medium priority
    HIGH = "high"  # High priority
    CRITICAL = "critical"  # Critical priority

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.LOW, "Low"),
            (cls.MEDIUM, "Medium"),
            (cls.HIGH, "High"),
            (cls.CRITICAL, "Critical"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class ProjectMemberRole:
    """Project member role constants"""

    OWNER = "owner"  # Project owner with full control
    MANAGER = "manager"  # Project manager with management permissions
    DEVELOPER = "developer"  # Developer with standard permissions
    TESTER = "tester"  # Tester with testing permissions
    VIEWER = "viewer"  # Viewer with read-only permissions

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.OWNER, "Owner"),
            (cls.MANAGER, "Manager"),
            (cls.DEVELOPER, "Developer"),
            (cls.TESTER, "Tester"),
            (cls.VIEWER, "Viewer"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.OWNER, cls.MANAGER, cls.DEVELOPER, cls.TESTER, cls.VIEWER]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# Task Related Constants
# =============================================================================


class TaskStatus:
    """Task status constants"""

    TODO = "todo"  # Task not started
    IN_PROGRESS = "in_progress"  # Task in progress
    IN_REVIEW = "in_review"  # Task under review
    TESTING = "testing"  # Task in testing phase
    DONE = "done"  # Task completed
    CLOSED = "closed"  # Task closed
    BLOCKED = "blocked"  # Task blocked by external dependencies

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.TODO, "To Do"),
            (cls.IN_PROGRESS, "In Progress"),
            (cls.IN_REVIEW, "In Review"),
            (cls.TESTING, "Testing"),
            (cls.DONE, "Done"),
            (cls.CLOSED, "Closed"),
            (cls.BLOCKED, "Blocked"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.TODO,
            cls.IN_PROGRESS,
            cls.IN_REVIEW,
            cls.TESTING,
            cls.DONE,
            cls.CLOSED,
            cls.BLOCKED,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()

    @classmethod
    def is_completed(cls, status):
        """Check if task status indicates completion"""
        return status in [cls.DONE, cls.CLOSED]

    @classmethod
    def is_incompleted(cls, status):
        """Check if task status indicates completion"""
        return status in [
            cls.TODO,
            cls.IN_PROGRESS,
            cls.IN_REVIEW,
            cls.TESTING,
            cls.BLOCKED,
        ]

    @classmethod
    def is_active(cls, status):
        """Check if task status indicates active work"""
        return status in [cls.TODO, cls.IN_PROGRESS, cls.IN_REVIEW, cls.TESTING]

    @classmethod
    def is_blocked(cls, status):
        """Check if task status indicates it is blocked"""
        return status == cls.BLOCKED

    @classmethod
    def is_review_required(cls, status):
        """Check if task status indicates it requires review"""
        return status in [cls.IN_REVIEW, cls.TESTING]

    @classmethod
    def is_open(cls, status):
        """Check if task status indicates it is open for work"""
        return status in [cls.TODO, cls.IN_PROGRESS, cls.IN_REVIEW, cls.TESTING]

    @classmethod
    def is_closed(cls, status):
        """Check if task status indicates it is closed"""
        return status in [cls.DONE, cls.CLOSED, cls.BLOCKED]

    @classmethod
    def get_next_status(cls, current_status):
        """Get the next logical status based on current status"""
        next_status_map = {
            cls.TODO: cls.IN_PROGRESS,
            cls.IN_PROGRESS: cls.IN_REVIEW,
            cls.IN_REVIEW: cls.TESTING,
            cls.TESTING: cls.DONE,
            cls.DONE: cls.CLOSED,
            cls.CLOSED: None,  # No next status after closed
            cls.BLOCKED: None,  # Blocked tasks do not progress
        }
        return next_status_map.get(current_status, None)

    @classmethod
    def get_incomplete_statuses(cls):
        return [cls.TODO, cls.IN_PROGRESS, cls.IN_REVIEW, cls.TESTING, cls.BLOCKED]

    @classmethod
    def get_complete_statuses(cls):
        return [cls.DONE, cls.CLOSED]


class TaskPriority:
    """Task priority constants"""

    LOW = "low"  # Low priority
    MEDIUM = "medium"  # Medium priority
    HIGH = "high"  # High priority
    CRITICAL = "critical"  # Critical priority
    BLOCKER = "blocker"  # Blocker priority

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.LOW, "Low"),
            (cls.MEDIUM, "Medium"),
            (cls.HIGH, "High"),
            (cls.CRITICAL, "Critical"),
            (cls.BLOCKER, "Blocker"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL, cls.BLOCKER]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class TaskType:
    """Task type constants"""

    FEATURE = "feature"  # Feature development
    BUG = "bug"  # Bug fix
    IMPROVEMENT = "improvement"  # Improvement or enhancement
    RESEARCH = "research"  # Research task
    DOCUMENTATION = "documentation"  # Documentation task
    TESTING = "testing"  # Testing task
    MAINTENANCE = "maintenance"  # Maintenance task

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.FEATURE, "Feature"),
            (cls.BUG, "Bug"),
            (cls.IMPROVEMENT, "Improvement"),
            (cls.RESEARCH, "Research"),
            (cls.DOCUMENTATION, "Documentation"),
            (cls.TESTING, "Testing"),
            (cls.MAINTENANCE, "Maintenance"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.FEATURE,
            cls.BUG,
            cls.IMPROVEMENT,
            cls.RESEARCH,
            cls.DOCUMENTATION,
            cls.TESTING,
            cls.MAINTENANCE,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# Calendar Related Constants
# =============================================================================


class EventType:
    """Event type constants"""

    MEETING = "meeting"  # Meeting event
    DEADLINE = "deadline"  # Deadline event
    MILESTONE = "milestone"  # Project milestone
    REMINDER = "reminder"  # Reminder event
    PERSONAL = "personal"  # Personal event
    HOLIDAY = "holiday"  # Holiday event
    TRAINING = "training"  # Training or learning event

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.MEETING, "Meeting"),
            (cls.DEADLINE, "Deadline"),
            (cls.MILESTONE, "Milestone"),
            (cls.REMINDER, "Reminder"),
            (cls.PERSONAL, "Personal"),
            (cls.HOLIDAY, "Holiday"),
            (cls.TRAINING, "Training"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.MEETING,
            cls.DEADLINE,
            cls.MILESTONE,
            cls.REMINDER,
            cls.PERSONAL,
            cls.HOLIDAY,
            cls.TRAINING,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class EventStatus:
    """Event status constants"""

    SCHEDULED = "scheduled"  # Event scheduled
    IN_PROGRESS = "in_progress"  # Event in progress
    COMPLETED = "completed"  # Event completed
    CANCELLED = "cancelled"  # Event cancelled
    POSTPONED = "postponed"  # Event postponed

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.SCHEDULED, "Scheduled"),
            (cls.IN_PROGRESS, "In Progress"),
            (cls.COMPLETED, "Completed"),
            (cls.CANCELLED, "Cancelled"),
            (cls.POSTPONED, "Postponed"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.SCHEDULED,
            cls.IN_PROGRESS,
            cls.COMPLETED,
            cls.CANCELLED,
            cls.POSTPONED,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class RecurrenceType:
    """Event recurrence type constants"""

    NONE = "none"  # No recurrence (one-time event)
    DAILY = "daily"  # Daily recurrence
    WEEKLY = "weekly"  # Weekly recurrence
    MONTHLY = "monthly"  # Monthly recurrence
    YEARLY = "yearly"  # Yearly recurrence
    WEEKDAYS = "weekdays"  # Monday to Friday only
    CUSTOM = "custom"  # Custom recurrence pattern

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.NONE, "No Recurrence"),
            (cls.DAILY, "Daily"),
            (cls.WEEKLY, "Weekly"),
            (cls.MONTHLY, "Monthly"),
            (cls.YEARLY, "Yearly"),
            (cls.WEEKDAYS, "Weekdays (Mon-Fri)"),
            (cls.CUSTOM, "Custom"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.NONE,
            cls.DAILY,
            cls.WEEKLY,
            cls.MONTHLY,
            cls.YEARLY,
            cls.WEEKDAYS,
            cls.CUSTOM,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()

    @classmethod
    def is_recurring(cls, value):
        """Check if recurrence type creates recurring events"""
        return value != cls.NONE

    @classmethod
    def get_frequency_description(cls, recurrence_type, interval=1):
        """Get human-readable frequency description"""
        descriptions = {
            cls.NONE: "One-time event",
            cls.DAILY: f"Every {interval} day(s)" if interval > 1 else "Daily",
            cls.WEEKLY: f"Every {interval} week(s)" if interval > 1 else "Weekly",
            cls.MONTHLY: f"Every {interval} month(s)" if interval > 1 else "Monthly",
            cls.YEARLY: f"Every {interval} year(s)" if interval > 1 else "Yearly",
            cls.WEEKDAYS: "Every weekday (Mon-Fri)",
            cls.CUSTOM: "Custom recurrence pattern",
        }
        return descriptions.get(recurrence_type, "Unknown")


class EventAttendeeStatus:
    """Event attendee status constants"""

    INVITED = "invited"  # Invited but not responded
    ACCEPTED = "accepted"  # Accepted invitation
    DECLINED = "declined"  # Declined invitation
    TENTATIVE = "tentative"  # Tentatively accepted
    NO_RESPONSE = "no_response"  # No response yet

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.INVITED, "Invited"),
            (cls.ACCEPTED, "Accepted"),
            (cls.DECLINED, "Declined"),
            (cls.TENTATIVE, "Tentative"),
            (cls.NO_RESPONSE, "No Response"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.INVITED, cls.ACCEPTED, cls.DECLINED, cls.TENTATIVE, cls.NO_RESPONSE]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()

    @classmethod
    def is_confirmed(cls, status):
        """Check if attendee status is confirmed (accepted or declined)"""
        return status in [cls.ACCEPTED, cls.DECLINED]


class EventReminder:
    """Event reminder time constants"""

    NONE = "none"  # No reminder
    AT_TIME = "at_time"  # At event time
    FIVE_MINUTES = "5_minutes"  # 5 minutes before
    TEN_MINUTES = "10_minutes"  # 10 minutes before
    FIFTEEN_MINUTES = "15_minutes"  # 15 minutes before
    THIRTY_MINUTES = "30_minutes"  # 30 minutes before
    ONE_HOUR = "1_hour"  # 1 hour before
    TWO_HOURS = "2_hours"  # 2 hours before
    ONE_DAY = "1_day"  # 1 day before
    ONE_WEEK = "1_week"  # 1 week before

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.NONE, "No Reminder"),
            (cls.AT_TIME, "At Event Time"),
            (cls.FIVE_MINUTES, "5 minutes before"),
            (cls.TEN_MINUTES, "10 minutes before"),
            (cls.FIFTEEN_MINUTES, "15 minutes before"),
            (cls.THIRTY_MINUTES, "30 minutes before"),
            (cls.ONE_HOUR, "1 hour before"),
            (cls.TWO_HOURS, "2 hours before"),
            (cls.ONE_DAY, "1 day before"),
            (cls.ONE_WEEK, "1 week before"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.NONE,
            cls.AT_TIME,
            cls.FIVE_MINUTES,
            cls.TEN_MINUTES,
            cls.FIFTEEN_MINUTES,
            cls.THIRTY_MINUTES,
            cls.ONE_HOUR,
            cls.TWO_HOURS,
            cls.ONE_DAY,
            cls.ONE_WEEK,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()

    @classmethod
    def get_minutes_before(cls, reminder_type):
        """Get minutes before event for reminder calculation"""
        minutes_map = {
            cls.NONE: 0,
            cls.AT_TIME: 0,
            cls.FIVE_MINUTES: 5,
            cls.TEN_MINUTES: 10,
            cls.FIFTEEN_MINUTES: 15,
            cls.THIRTY_MINUTES: 30,
            cls.ONE_HOUR: 60,
            cls.TWO_HOURS: 120,
            cls.ONE_DAY: 1440,  # 24 * 60
            cls.ONE_WEEK: 10080,  # 7 * 24 * 60
        }
        return minutes_map.get(reminder_type, 0)


# =============================================================================
# Notification Related Constants
# =============================================================================


class NotificationType:
    """Notification type constants"""

    INFO = "info"  # Information notification
    WARNING = "warning"  # Warning notification
    ERROR = "error"  # Error notification
    SUCCESS = "success"  # Success notification

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.INFO, "Info"),
            (cls.WARNING, "Warning"),
            (cls.ERROR, "Error"),
            (cls.SUCCESS, "Success"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.INFO, cls.WARNING, cls.ERROR, cls.SUCCESS]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class NotificationChannel:
    """Notification channel constants"""

    EMAIL = "email"  # Email notification
    IN_APP = "in_app"  # In-app notification
    SMS = "sms"  # SMS notification
    PUSH = "push"  # Push notification

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.EMAIL, "Email"),
            (cls.IN_APP, "In-App"),
            (cls.SMS, "SMS"),
            (cls.PUSH, "Push"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.EMAIL, cls.IN_APP, cls.SMS, cls.PUSH]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# File Related Constants
# =============================================================================


class FileType:
    """File type constants"""

    DOCUMENT = "document"  # Document file
    IMAGE = "image"  # Image file
    VIDEO = "video"  # Video file
    AUDIO = "audio"  # Audio file
    ARCHIVE = "archive"  # Archive file
    CODE = "code"  # Source code file
    OTHER = "other"  # Other file type

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.DOCUMENT, "Document"),
            (cls.IMAGE, "Image"),
            (cls.VIDEO, "Video"),
            (cls.AUDIO, "Audio"),
            (cls.ARCHIVE, "Archive"),
            (cls.CODE, "Code"),
            (cls.OTHER, "Other"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.DOCUMENT,
            cls.IMAGE,
            cls.VIDEO,
            cls.AUDIO,
            cls.ARCHIVE,
            cls.CODE,
            cls.OTHER,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class AttachmentContext:
    """Attachment context constants"""

    PROJECT = "project"  # Project attachment
    TASK = "task"  # Task attachment
    COMMENT = "comment"  # Comment attachment
    USER_PROFILE = "user_profile"  # User profile attachment

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.PROJECT, "Project"),
            (cls.TASK, "Task"),
            (cls.COMMENT, "Comment"),
            (cls.USER_PROFILE, "User Profile"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.PROJECT, cls.TASK, cls.COMMENT, cls.USER_PROFILE]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# Activity Log Related Constants
# =============================================================================


class ActivityAction:
    """Activity action constants"""

    CREATE = "create"  # Created resource
    UPDATE = "update"  # Updated resource
    DELETE = "delete"  # Deleted resource
    VIEW = "view"  # Viewed resource
    LOGIN = "login"  # User login
    LOGOUT = "logout"  # User logout
    ASSIGN = "assign"  # Assigned resource
    UNASSIGN = "unassign"  # Unassigned resource
    COMMENT = "comment"  # Added comment
    UPLOAD = "upload"  # Uploaded file
    DOWNLOAD = "download"  # Downloaded file

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.CREATE, "Create"),
            (cls.UPDATE, "Update"),
            (cls.DELETE, "Delete"),
            (cls.VIEW, "View"),
            (cls.LOGIN, "Login"),
            (cls.LOGOUT, "Logout"),
            (cls.ASSIGN, "Assign"),
            (cls.UNASSIGN, "Unassign"),
            (cls.COMMENT, "Comment"),
            (cls.UPLOAD, "Upload"),
            (cls.DOWNLOAD, "Download"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.CREATE,
            cls.UPDATE,
            cls.DELETE,
            cls.VIEW,
            cls.LOGIN,
            cls.LOGOUT,
            cls.ASSIGN,
            cls.UNASSIGN,
            cls.COMMENT,
            cls.UPLOAD,
            cls.DOWNLOAD,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class ResourceType:
    """Resource type constants"""

    USER = "user"  # User resource
    PROJECT = "project"  # Project resource
    TASK = "task"  # Task resource
    EVENT = "event"  # Event resource
    COMMENT = "comment"  # Comment resource
    FILE = "file"  # File resource
    CALENDAR = "calendar"  # Calendar resource

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.USER, "User"),
            (cls.PROJECT, "Project"),
            (cls.TASK, "Task"),
            (cls.EVENT, "Event"),
            (cls.COMMENT, "Comment"),
            (cls.FILE, "File"),
            (cls.CALENDAR, "Calendar"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [
            cls.USER,
            cls.PROJECT,
            cls.TASK,
            cls.EVENT,
            cls.COMMENT,
            cls.FILE,
            cls.CALENDAR,
        ]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


# =============================================================================
# Permission Related Constants
# =============================================================================


class Permission:
    """Permission constants"""

    READ = "read"  # Read permission
    WRITE = "write"  # Write permission
    DELETE = "delete"  # Delete permission
    ADMIN = "admin"  # Admin permission

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.READ, "Read"),
            (cls.WRITE, "Write"),
            (cls.DELETE, "Delete"),
            (cls.ADMIN, "Admin"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.READ, cls.WRITE, cls.DELETE, cls.ADMIN]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()


class AccessLevel:
    """Access level constants"""

    PUBLIC = "public"  # Public access
    PRIVATE = "private"  # Private access
    TEAM = "team"  # Team access
    ORGANIZATION = "organization"  # Organization access

    @classmethod
    def choices(cls):
        """Get all available choices as list of tuples"""
        return [
            (cls.PUBLIC, "Public"),
            (cls.PRIVATE, "Private"),
            (cls.TEAM, "Team"),
            (cls.ORGANIZATION, "Organization"),
        ]

    @classmethod
    def values(cls):
        """Get all available values as list"""
        return [cls.PUBLIC, cls.PRIVATE, cls.TEAM, cls.ORGANIZATION]

    @classmethod
    def is_valid(cls, value):
        """Check if value is valid"""
        return value in cls.values()
