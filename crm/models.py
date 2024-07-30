from pydantic import BaseModel
from datetime import datetime, date


class User(BaseModel):
    login: str
    firstName: str
    lastName: str
    email: str
    phone: str
    roles: list


class Reminder:
    pass


class Comment:
    comment: str
    dataTime: datetime | None = None
    addedBy: User | None = None
    details: str | None = None


class WeekDays:
    Sunday: bool = False
    Monday: bool = False
    Tuesday: bool = False
    Wednesday: bool = False
    Thursday: bool = False
    Friday: bool = False
    Saturday: bool = False


class Group:
    id: int
    name: str
    teacher: str
    whatsApp: str | None = None
    slack: str | None = None
    skype: str | None = None
    startDate: date | None = None
    expectedFinishDate: date | None = None
    lessonsDays: WeekDays
    webinarDays: WeekDays
    studentList: list
    reminders: list
    active: bool = False
    autoArchive: bool = False


class Payment:
    id: int
    date: datetime
    type: str
    amount: float
    details: str | None = None
    description: str


class Contact(BaseModel):
    id: int
    name: str
    surname: str | None = None
    email: str | None = None
    phone: str
    city: str | None = None
    course: str | None = None
    source: str | None = None
    status: str | None = None
    comments: list | None = []
    reminder: Reminder | None = None


class Student(Contact):
    teudatZeut: int
    group: Group
    groupHistory: list
    courseFee: int
    payments: list
    documents: bool


class Lecturer(BaseModel):
    pass
