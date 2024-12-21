"""Data Formatter for the heitzfit4 integration."""

import logging
from datetime import datetime

from .const import (
    RESERVATION_DESC_MAX_LENGTH,
)

_LOGGER = logging.getLogger(__name__)


def format_displayed_activity(activity):
    return activity._task.label


# def format_activity(activity, lunch_break_time):
def format_activity(activity):
    return {
        "start_at": activity.start,
        "end_at": activity.end,
        "start_time": activity.start.strftime("%H:%M"),
        "end_time": activity.end.strftime("%H:%M"),
        # "activity": format_displayed_activity(activity),
        "activity": activity._task.label,
        "room": activity._room.label,
        # "canceled": activity.canceled,
        # "status": activity.status,
        "background_color": activity._task.colorHex,
        "place_max": activity._stats.active,
        "place_reserved": activity._stats.inQueue,
        # "teacher_name": activity.teacher_name,
        # "teacher_names": activity.teacher_names,
        # "classrooms": activity.classrooms,
        # "outing": activity.outing,
        # "memo": activity.memo,
        # "group_name": activity.group_name,
        # "group_names": activity.group_names,
        # "exempted": activity.exempted,
        # "virtual_classrooms": activity.virtual_classrooms,
        # "num": activity.num,
        # "detention": activity.detention,
        # "test": activity.test,
        # "is_morning": activity.start.time() < lunch_break_time,
        # "is_afternoon": activity.start.time() >= lunch_break_time,
    }


# def format_attachment_list(attachments):
#     return [
#         {
#             "name": attachment.name,
#             "url": attachment.url,
#             "type": attachment.type,
#         }
#         for attachment in attachments
#     ]


# def format_reservation(reservation) -> dict:
#     return {
#         "date": reservation.date,
#         "subject": reservation.subject.name,
#         "short_description": (reservation.description)[0:reservation_DESC_MAX_LENGTH],
#         "description": (reservation.description),
#         "done": reservation.done,
#         "background_color": reservation.background_color,
#         # "files": format_attachment_list(reservation.files),
#     }


# def format_grade(grade) -> dict:
#     return {
#         "date": grade.date,
#         "subject": grade.subject.name,
#         "comment": grade.comment,
#         "grade": grade.grade,
#         "out_of": str(grade.out_of).replace(".", ","),
#         "default_out_of": str(grade.default_out_of).replace(".", ","),
#         "grade_out_of": grade.grade + "/" + grade.out_of,
#         "coefficient": str(grade.coefficient).replace(".", ","),
#         "class_average": str(grade.average).replace(".", ","),
#         "max": str(grade.max).replace(".", ","),
#         "min": str(grade.min).replace(".", ","),
#         "is_bonus": grade.is_bonus,
#         "is_optionnal": grade.is_optionnal,
#         "is_out_of_20": grade.is_out_of_20,
#     }


# def format_absence(absence) -> dict:
#     return {
#         "from": absence.from_date,
#         "to": absence.to_date,
#         "justified": absence.justified,
#         "hours": absence.hours,
#         "days": absence.days,
#         "reason": str(absence.reasons)[2:-2],
#     }


# def format_delay(delay) -> dict:
#     return {
#         "date": delay.date,
#         "minutes": delay.minutes,
#         "justified": delay.justified,
#         "justification": delay.justification,
#         "reasons": str(delay.reasons)[2:-2],
#     }


# def format_evaluation(evaluation) -> dict:
#     return {
#         "name": evaluation.name,
#         "domain": evaluation.domain,
#         "date": evaluation.date,
#         "subject": evaluation.subject.name,
#         "description": evaluation.description,
#         "coefficient": evaluation.coefficient,
#         "paliers": evaluation.paliers,
#         "teacher": evaluation.teacher,
#         "acquisitions": [
#             {
#                 "order": acquisition.order,
#                 "name": acquisition.name,
#                 "abbreviation": acquisition.abbreviation,
#                 "level": acquisition.level,
#                 "domain": acquisition.domain,
#                 "coefficient": acquisition.coefficient,
#                 "pillar": acquisition.pillar,
#                 "pillar_prefix": acquisition.pillar_prefix,
#             }
#             for acquisition in evaluation.acquisitions
#         ],
#     }


# def format_average(average) -> dict:
#     return {
#         "average": average.student,
#         "class": average.class_average,
#         "max": average.max,
#         "min": average.min,
#         "out_of": average.out_of,
#         "default_out_of": average.default_out_of,
#         "subject": average.subject.name,
#         "background_color": average.background_color,
#     }


# def format_punishment(punishment) -> dict:
#     return {
#         "date": punishment.given.strftime("%Y-%m-%d"),
#         "subject": punishment.during_activity,
#         "reasons": punishment.reasons,
#         "circumstances": punishment.circumstances,
#         "nature": punishment.nature,
#         "duration": str(punishment.duration),
#         "reservation": punishment.reservation,
#         "exclusion": punishment.exclusion,
#         "during_activity": punishment.during_activity,
#         "reservation_documents": format_attachment_list(punishment.reservation_documents),
#         "circumstance_documents": format_attachment_list(
#             punishment.circumstance_documents
#         ),
#         "giver": punishment.giver,
#         "schedule": [
#             {
#                 "start": schedule.start,
#                 "duration": str(schedule.duration),
#             }
#             for schedule in punishment.schedule
#         ],
#         "schedulable": punishment.schedulable,
#     }


# def format_food_list(food_list) -> dict:
#     formatted_food_list = []
#     if food_list is None:
#         return formatted_food_list

#     for food in food_list:
#         formatted_food_labels = []
#         for label in food.labels:
#             formatted_food_labels.append(
#                 {
#                     "name": label.name,
#                     "color": label.color,
#                 }
#             )
#         formatted_food_list.append(
#             {
#                 "name": food.name,
#                 "labels": formatted_food_labels,
#             }
#         )

#     return formatted_food_list


# def format_menu(menu) -> dict:
#     return {
#         "name": menu.name,
#         "date": menu.date.strftime("%Y-%m-%d"),
#         "is_lunch": menu.is_lunch,
#         "is_dinner": menu.is_dinner,
#         "first_meal": format_food_list(menu.first_meal),
#         "main_meal": format_food_list(menu.main_meal),
#         "side_meal": format_food_list(menu.side_meal),
#         "other_meal": format_food_list(menu.other_meal),
#         "cheese": format_food_list(menu.cheese),
#         "dessert": format_food_list(menu.dessert),
#     }


# def format_information_and_survey(information_and_survey) -> dict:
#     return {
#         "author": information_and_survey.author,
#         "title": information_and_survey.title,
#         "read": information_and_survey.read,
#         "creation_date": information_and_survey.creation_date,
#         "start_date": information_and_survey.start_date,
#         "end_date": information_and_survey.end_date,
#         "category": information_and_survey.category,
#         "survey": information_and_survey.survey,
#         "anonymous_response": information_and_survey.anonymous_response,
#         "attachments": format_attachment_list(information_and_survey.attachments),
#         "template": information_and_survey.template,
#         "shared_template": information_and_survey.shared_template,
#         "content": information_and_survey.content,
#     }
