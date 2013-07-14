todo
====

Simple CLI todo-manager

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
	
todo dates [OPTIONS]
	Shows dates for current day and does some control of it.
	-f FILE, --file=FILE   path to the date file. Format is described above.
	-m, --missed           shows missed tasks.
	-t, --today            shows current tasks for today.
	-n, --number           adds number to each task which can be used with options --finish etc.
	-c N, --complete=N     marks task with number N of today as completed (for today).
	--next=N               prints tasks for next N days (excluding current).
	--next-no-mask=N       prints tasks for next N days (excluding current) not counting dates which are masks.
	-p, --purge            purge finished tasks (those which are completed and has plain date without mask).

todo project [OPTIONS]
	Prints some to-do info for .git or .svn project.
	-t, --todo     Searches for TODO and FIXME entries and prints lines.
	-l, --license  Searches for LICENSE or LICENCE file in the project root dir.
	-r, --readme   Searches for README* file in the project root dir.
	-d, --doxyfile Searches for Doxyfile in the project root dir.

Date file format:
	DATE [(DATE_OF_COMPLETION)] - TASK
	DATE is a date in format: MONTH_NAME DAY YEAR. MONTH_NAME is a three letters of month in English locale:
		Jun 01 2014
	Every part of date could contain '*', which means that this tasks is valid on each day, each month or each year respectively:
		* 01 2014 - first day of each month in 2014.
		* 01 * - first day of each month of each year.
		* * 2014 - each day of 2014 year.
		Jun * * - each day of June.
	DAY part could also contain three-letter name of weekday (Mon..Sun):
		Jun Mon * - each Monday of June.
		* Sun * - each Sunday of each month of each year.
	Task is considered on-going when current date matches DATE mask and when there is no DATE_OF_COMPLETION (or it is ealier or equal than current date).
	Task is considered missed, when current date matches DATE mask and there is DATE_OF_COMPLETION, earlier than current day and this interval has some dates that satisfies DATE mask. Every of that dates considered missed tasks.
	Task is considered finished, when DATE is plain date (no mask) and there is DATE_OF_COMPLETION.
	DATE_OF_COMPLETION is inserted automatically each time user marks task as completed.

		
