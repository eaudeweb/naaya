To use the Naaya Survey product two steps must be followed:
1. Create a Survey Template in the portal administration, in the survey templates administration area.
2. Add somewhere in the portal a survey of that type and let responds take it.



	Creating a Survey Template
	----------------------

	Go to the portal administration page and click on the "Survey templates management" link. In this section you will be able to manage (add, edit, delete) the survey templates.
	To add a new survey template, choose a title for it and click on "Add survey template" and edit it. Next you will be able to add questions.


		Questions
		---------

		The following types of questions are supported:
		- Multiple Choice - One Answer:
			- Combobox
			- Radio buttons
			- Radio matrix (group of questions with one answer per row)
		- Multiple Choice - Multiples Answers:
			- Checkboxes
			- Checkbox matrix (group of questions with multiple answers per row)
		- Single line text  (free text input box)
		- Paragraph text (multiple line answer, used for longer responses)
		- Date (for date type answers)
		- File (for uploading files)
	
		If you need to add descriptive text, for example to describe some sections of the survey, you can use the "Label" question, which has no answer. The respondent will see only the descriptive text.

		After adding a question, you can further customize it (set the available choices) by clicking on the "Edit" button, or you can see how it will look like by clicking on its title. To see how the survey will look like, use the "Preview survey template" button.

		To change the order of the questions, change the "sort order" column accordingly and press the "Set sort order" button.


		Reports
		-------

		To analyze the results of the survey, you need to create one or more reports. Click on the "Reports" tab to go to the reports management section.

		To add a new report, choose a title for it and click on "Add report". To change its description click on "Edit". To configure the statistics included in the report click on its title.

		Now choose the question that will be included in the report and then what kind of statistics would you like. There are 2 major types of statistics: numerical (tabular) and graphical (charts).



	Using a Survey Template
	-------------------

	Go to the folder where you want to publish your survey. Click on the "Subobjects" button. Make sure that "Survey" is selected in the list of object types, click "Save changes" and then go back to index. Note: this step is needs to be done only once per folder.

	From the list of available Naaya types select "Survey" and then choose the survey template that you want to use. You can also set the release date and the expiration date. The release date works just like for the rest of the Naaya types. The expiration date is the date after which the survey can't be taken anymore.


		Taking the survey
		-----------------

		Send the link of the survey to the respondents. When a respondent answers, the owner of the survey will receive a notification email, which includes a link to the newly added answer.


		Analyzing the results
		---------------------

		To view the list with all the responses click on the "View answers" button from the survey's page. Then click on the answer that you want to see.

		To view the reports click on the "View reports" button from the survey's page. A table with all the available reports for that survey template will appear. Click on the report that you want to see.





	Administration
	--------------

	The respondents must have the "Naaya - Add Naaya Survey Answer" permission.
	Because the basic view permission is too general, two other permissions are required to view the reports and the list of answers: "Naaya - View Naaya Survey Reports" and "Naaya - View Naaya Survey Answers".
