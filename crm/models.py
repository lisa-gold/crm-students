from pydantic import BaseModel
from datetime import datetime, date


class User(BaseModel):
    login: str | None = None
    password: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    phone: str | None = None
    roles: list | None = ['USER']


class Reminder(BaseModel):
    description: str
    when: datetime | None = None
    status: bool | None = True  # True - active, False - done
    # todo: add what is needed


class Comment(BaseModel):
    comment: str
    dateTime: datetime | None = None
    addedBy: User | None = None
    details: str | None = None


class WeekDays(BaseModel):
    Sunday: bool = False
    Monday: bool = False
    Tuesday: bool = False
    Wednesday: bool = False
    Thursday: bool = False
    Friday: bool = False
    Saturday: bool = False


class Group(BaseModel):
    id: int | None = None
    name: str | None = None
    teacher: str | None = None
    whatsApp: str | None = None
    slack: str | None = None
    skype: str | None = None
    startDate: date | None = None
    expectedFinishDate: date | None = None
    lessonsDays: WeekDays | None = None
    webinarDays: WeekDays | None = None
    studentsList: list[int] | None = []
    reminders: list[Reminder] | None = []
    active: bool = False
    autoArchive: bool = False


class Payment(BaseModel):
    id: int
    date: datetime
    type: str
    amount: float
    details: str | None = None
    description: str


class Contact(BaseModel):
    id: int | None = None
    name: str | None = None
    surname: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    course: str | None = None
    source: str | None = None
    status: str | None = 'LEAD'
    comments: list[Comment] | None = []
    reminders: list[Reminder] | None = []


class Student(Contact):
    teudatZeut: int | None = None
    group: int | None = None
    groupsHistory: list[int] | None = []
    courseFee: int | None = None
    payments: list[Payment] | None = []
    documents: bool | None = None


class Lecturer(BaseModel):
    pass
