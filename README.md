todo
====

Simple CLI todo-manager

Use cases
---------

Shows some motto or habit (using list of them and switching on start of each month).

Dated tasks:
Adding, removing, editing tasks. Changing date, changing text.
Showing current tasks, missed tasks, tasks for next few days, all tasks.
Tasks with wildcards: each 1 of month, each Monday, each Sunday. They need to be completed (marked or removed, dunno).

showing icon in tray when some condition is executing (like having unfinished tasks for today, dated tasks or such).

Alarms: sound and notification (tray and pop-up).
the same: adding, removing, editing time and text.

print TODO grepped in current dir.
Checks LICEN[CS]E, README\*, Doxyfile in current dir or in top-level git-repo dir (or svn-project)

Move selected file (or all files in dir) to specified dir (ensure it existence)

Design document
---------------

Usage:

todo shuffle [OPTIONS] [PATTERN]
	Prints list of files in current (working directory).
	Prints either all files or ones specified by PATTERN.
	Options:
		-c N, --count=N     print only N first files from shuffled list.

todo tree [OPTIONS] DIR
	Prints tree view of specified directory. Only one level.
	-e PATTERN, --exclude PATTERN   excludes files and dirs which meet PATTERN. Can have several entry of this option.

todo eightball
	Emulates magic 8-ball: prints random saying.

todo collect [OPTIONS] [files]
	Collects tasks from specified files. Tries to guess encoding (and re-encode to utf-8) and line-ending format.
	-o FILE, --otl=FILE  path to the OTL file. Collected tasks will be appended to it's end. Required option.
	-r, --remove         remove files after collecting.
	-x, --checkbox       prepends all tasks with outliner-style checkboxes ([_]).

todo otl [OPTIONS]
	Prints various information from specified OTL-file.
	-o FILE, --otl=FILE         path to the OTL file. Required option.
	-t, --top-only              shows only top-level tasks.
	-a STRING, --after=STRING   prints tasks found only below line which contains STRING.
	-b STRING, --before=STRING  prints tasks found only above line which contains STRING.
	-p, --percent               instead of list of tasks print percentage of completion (right next to checkbox) with respect to total percents (100% for each task).
                                tasks without percentage (either one-level only or without that number) will be counted as 0% when unchecked or 100% when checked.
								Excludes --random.
	-r, --random                Prints random task from the list. Excludes --percent.
	-u, --unsolved              Prints first unsolved sub-task from each top-level task (works only with --random).
	
