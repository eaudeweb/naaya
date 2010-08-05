Experimental product - use it at your own risk!



Naaya Cron Tool
---------------

This tool can be used to run periodic jobs on each Naaya site from a Zope
instance.

To set the jobs go to ZMI -> /naaya_admin_tool -> cron_tool -> "Properties" tab
and modify the "Jobs" property accordingly. Each line of the property
represents a job. The format of a job is "period python_code_to_execute".
The period is expressed in minutes. You can use any Python code you want. The
"site" variable represents the Naaya site on which the job is run.

Jobs example:
10 site.cleanupUnsubmittedObjects(site.get_site_uid())
20 site.notifications_cron_job(site.get_site_uid(), time_to_run="daily")

You will have to call periodicaly (at every 10 minutes) this URL:
http://admin:admin@localhost:8080/naaya_admin_tool/cron_tool/runJobs
which will run all (only!) the jobs that need to be run.

To reset the timers use this URL:
http://admin:admin@localhost:8080/naaya_admin_tool/cron_tool/resetTimers
