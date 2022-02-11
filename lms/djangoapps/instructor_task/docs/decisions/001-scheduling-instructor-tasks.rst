==========================
Scheduled Instructor Tasks
==========================

Status
------

Draft

Background
----------

One of the most requested features in edx-platform has been the ability to schedule an email message to be sent at a specified date and time through the Instructor Dashboard's Bulk Course Email tool. These email messages are sent as an instructor task. Today, edx-platform does not have the ability to support scheduling of instructor tasks. When an instructor task is created we attempt to execute the task immediately.

This ADR covers details on the proposed modeling of a scheduled instructor task. A subsequent ADR will focus on the processing of scheduled instructor tasks.

Decision
--------

* We will introduce a new ``InstructorTaskSchedule`` model to track the (optional) schedule of an instructor task.
* We will extend the existing ``InstructorTask`` model with a new (nullable) column to link an instructor task to its schedule.
* We will introduce a new **SCHEDULED** state that will be used by the ``InstructorTask`` model to denote a task that has been scheduled for execution at a later date and time.
* Instructor tasks without a schedule will continue to be executed immediately.

The ``InstructorTaskSchedule`` model
====================================

This new model that will be responsible for tracking the due date of an instructor task, as well as some information needed to process the tasks later. The model will have two fields:

* **due** (DateTime): The date and time to execute the associated Instructor Task.
* **task_args** (TextField): This will store information required to execute the task later. The source data is in the form of a dictionary that will be converted to text for storage in the database.

Extending the ``InstructorTask`` model
======================================

We will extend the existing ``InstructorTask`` model with a new nullable column named **schedule**. This field will have a OneToOne relation to the ``InstructorTaskSchedule`` model. An instructor task is a one-time task and thus should only ever have a single schedule attributed to it.

New State
=========

The ``InstructorTask`` model currently uses two custom states (**QUEUEING** and **PROGRESS**) to describe the current status of a task. We will introduce a third custom state named **SCHEDULED** to represent the status of a scheduled instructor task.

Rejected Solutions
------------------

Celery: the ``eta`` and ``countdown`` arguments
===============================================

Celery provides two `optional arguments`_ (**eta** and **countdown**) that can delay the execution of a task. 

* **eta**: A specific date and time describing the earliest moment a task should be executed.
* **countdown**: How many seconds Celery should wait before a task should be executed.

The Celery worker process holds these delayed tasks in memory aside from any non-delayed tasks. This can be memory intensive. We found several well documented accounts of performance issues related to using these options. Unless the tasks are only delayed for just a few minutes, it seems best to avoid this solution.

Object Inheritance
==================

We considered creating a new ``ScheduledInstructorTask`` model that inherits from the existing ``InstructorTask`` model. After reading about how Django treats model inheritance, we decided against this route. Using (single-table or multi-table) inheritance didn't provide any clear or discernable advantages (and there were plenty of documented reasons *not* to use a multi-table inheritance approach).

.. _optional arguments: https://docs.celeryproject.org/en/latest/userguide/calling.html?highlight=countdown#eta-and-countdown 
