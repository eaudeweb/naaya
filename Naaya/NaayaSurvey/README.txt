This product lets the portal administrator create surveys, that both authenticated and anonymous users can take.

To be able to use it in a Naaya portal, enter the ZMI of the portal and add a Naaya Survey Tool in its root.

	Creating a survey
	-----------------

	Go the folder where you want to create it. Click on the Subobjects button. Make sure that Survey is selected in the list of object types, click "Save changes" and then go back to index. Note: this step needs to be done only once per folder. Now select "Survey" from the "Type to add" combobox and a form for creating a survey will appear.

	On the top of the survey there are buttons for editing the metadata of the survey (e.g. title, description), attachments, questions and reports.

		Metadata
		--------

		You can set a release date and an expiration date. The release date works just like for the rest of the Naaya types. The expiration date is the date after which the survey can't be taken anymore.

		Attachments
		-----------

		When the survey is about some documents (e.g. some EU directives), the user can upload these documents as attachments. When the respondent will take the survey, the attachments will appear at the top of the page (bellow the description).

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

		After adding a question, you can further customize it (set the available choices) by clicking on the "Edit" button, or you can see how it will look like by clicking on its title.

		To change the order of the questions, change the "sort order" column accordingly and press the "Set sort order" button.

		Reports
		-------

		To analyze the results of the survey, you need to create one or more reports. Click on the "Edit Reports" button to go to the reports management section.

		To add a new report, choose a title for it and click on "Add report". To change its description click on "Edit". To configure the statistics included in the report click on its title. Now choose the question that will be included in the report and then what kind of statistics would you like. There are 2 major types of statistics: numerical (tabular) and graphical (charts).

		Because adding a statistic one by one would take too much time for a complex survey with many questions, there is the possibility of creating a complete report with all the question - statistic combinations. To create this report, choose a title and click on the "Generate full report" button.


	Taking the survey
	-----------------

	Send the link of the survey to the respondents. When a respondent answers, the owner of the survey will receive a notification email, which includes a link to the newly added answer. Authenticated respondents can receive a notification too, if they wish to.

	To prevent spam, captcha is used for anonymous users. Authenticated users are permitted to answer only once, but they can change their answers anytime they wish too (if the survey has not expired).


	Analyzing the results
	---------------------

	To view the list with all the responses click on the "View answers" button from the survey's page. Then click on the answer that you want to see.

	To view the reports click on the "View reports" button from the survey's page. A table with all the available reports for that survey will appear. Click on the report that you want to see.



	Administration
	--------------

		Security
		--------

		The following permissions exist:
		- Add permissions:
			- 'Naaya - Add Naaya Survey Tool': used for adding the survey tool
			- 'Naaya - Add Naaya Survey Template'; by default it's given to Manager and Administrator
			- 'Naaya - Add Naaya Survey Report': used for reports; by default it's given to Manager and Administrator
			- 'Naaya - Add Naaya Statistic': used for reports; by default it's given to Manager and Administrator
			- 'Naaya - Add Naaya Survey Questionnaire': create a survey;  by default it's given to Contributor
			- 'Naaya - Add Naaya Survey Attachment; by default it's given to Manager and Administrator'
			- 'Naaya - Add Naaya Mega Survey': create a survey;  by default it's given to Contributor
			- 'Naaya - Add Naaya Survey Answer': answer/take a survey; by default it's given to all users (Anonymous)
		- Edit/Manage permissions:
			- 'Naaya - Manage Naaya Survey Template'; by default it's given to Manager and Administrator
			- the generic *edit published object* permission lets you edit *Survey Questionnaires*, *Mega Surveys*, questions and reports
		- View permissions:
			- 'Naaya - View Naaya Survey Answers': view the list of answers; by default it's given to Contributor
			- 'Naaya - View Naaya Survey Reports': view the reports;  by default it's given to all users (Authenticated and Anonymous)
		Also the 'Naaya - Add Naaya Widgets' permission from NaayaWidgets is given by default to Manager and Administrator.

		N.B.: the 'Naaya - Manage Naaya Survey Template' permission doesn't apply to objects (e.g. questions, reports) inside a *Survey Template*! You'll need to give the *edit published object* permission for the *Survey Tool* (/portal_survey) only to trusted users.

		When a "Survey Tool" is added, the security of the site will be configured as described above.
		Unsupported: you can also call through the web the manage_configureSite method, e.g. "/portal_survey/manage_configureSite".
