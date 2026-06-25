"""
OOP data models for DevTrack.

These are plain Python classes (NOT Django ORM models), because we store
data in JSON files instead of a database. They demonstrate:
  - Abstraction      -> BaseEntity is an abstract base class (ABC)
  - Inheritance      -> Reporter and Issue inherit from BaseEntity
  - Polymorphism     -> CriticalIssue / LowPriorityIssue override describe()
  - Encapsulation    -> each class validates its own data via validate()
"""

from abc import ABC, abstractmethod
from datetime import datetime


# Allowed values, defined once so validation and the rest of the app agree.
VALID_STATUSES = ('open', 'in_progress', 'resolved', 'closed')
VALID_PRIORITIES = ('low', 'medium', 'high', 'critical')


class BaseEntity(ABC):
    """Abstract base shared by every entity in the system.

    'Abstract' means you cannot create a BaseEntity directly; it only exists
    to be inherited from. Any subclass MUST provide its own validate().
    """

    @abstractmethod
    def validate(self):
        """Subclasses must implement their own validation rules."""
        pass

    def to_dict(self):
        """Turn the object's attributes into a plain dict (for JSON output)."""
        return {
            key: value
            for key, value in self.__dict__.items()
        }


class Reporter(BaseEntity):
    """A person who files issues."""

    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError('Name cannot be empty')
        if '@' not in self.email:
            raise ValueError('Invalid email')


class Issue(BaseEntity):
    """A bug report or task filed by a Reporter (medium/high priority)."""

    def __init__(self, id, title, description, status, priority,
                 reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        # created_at is optional: generate it now if the caller didn't pass one.
        self.created_at = created_at or str(datetime.now())

    def validate(self):
        if not self.title:
            raise ValueError('Title cannot be empty')
        if self.status not in VALID_STATUSES:
            raise ValueError('Invalid status')
        if self.priority not in VALID_PRIORITIES:
            raise ValueError('Invalid priority')

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    """A critical issue. Overrides describe() with an urgent message."""

    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    """A low-priority issue. Overrides describe() with a relaxed message."""

    def describe(self):
        return f"{self.title} — low priority, handle when free"
