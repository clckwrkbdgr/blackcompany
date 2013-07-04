todo
====

Simple CLI todo-manager

Design
------

Shuffle command: checks files in given directory and show shuffled list or part of it. Using pattern (regexp).
Eightball command: shows random saying like Fallout 2 eightball.
Collects tasks from files in given places, converting them to utf-8 and linux-linebreaks, removing them. Stores tasks into specified OTL-file, prepending them with [ ] 
Shows tasks within OTL, which are after some specified line (or line containing specified string). Showing only top tasks or all tasks.
Calculating solved tasks (percents if present) and show info in format SOLVED/TOTAL
Shows tree of specified dir, with option to ignore some entries.
Shows random task from OTL: top task or first unsolved for each top task.
Shows some motto or habit (using list of them and switching on start of each month).


Dated tasks:
Adding, removing, editing tasks. Changing date, changing text.
Showing current tasks, missed tasks, tasks for next few days, all tasks.
Tasks with wildcards: each 1 of month, each Monday, each Sunday. They need to be completed (marked or removed, dunno).

showing icon in tray when some condition is executing (like having unfinished tasks for today, dated tasks or such).

Alarms: sound and notification (tray and pop-up).
the same: adding, removing, editing time and text.
