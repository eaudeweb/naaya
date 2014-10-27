This component lets content contributors create surveys that both authenticated and anonymous users can take. A survey is a research instrument consisting of a series of questions for the purpose of gathering information from respondents. The respondents are usually part of a community with relevant knowledge in the area of interest of your survey and they can be from a restricted group (authenticated users only) or part of the general public.

The answers to the survey can be analysed individually or they can be aggregated as statistics in reports. Both numerical and graphical statistics exist.

This is an optional component that may not come by default with your portal installation, but that can be added later. If you use it for the first time in a Naaya portal, enter the ZMI and add a Naaya Survey Tool in its root. This tool makes basic configurations in the portal, that allow surveys later defined to be indexed by searches, have a default notification mechanism and makes a default assignation of relevant permissions to roles (see the section about survey security).

Creating a survey
-----------------

A survey can be added inside Naaya folders, just like any other content type (e.g. Naaya Document, Naaya News).

Go the folder where you want to create it and click on the Subobjects button. Make sure that Survey is selected in the list of object types, click "Save changes" and then go back to the folder index. Note: this step needs to be done only once per folder if the survey type is not a  default data type for the entire portal. Now select "Survey" from the "Type to add" combobox and a form for creating a survey will appear.

The administrators can change the survey (e.g. title, description), its attachments, the composing questions and its automatically generated reports by using the upper toolbar buttons.


	Survey editing
	--------------
	Beside the standard properties for Naaya content, the survey has a release and an expiration date. No one can take the survey before its release date or after its expiration date.

		Attachments
		-----------

		When taking the survey implies having read some background documentation,  the user managing the survey will upload these documents as attachments. When respondents take the survey, the attachments appear at the top of the page (bellow the description).

		Questions
		---------

		The following types of questions are supported:
		 * Multiple choice - one answer:
		   - Combobox
		   - Radio buttons
		   - Radio matrix (group of questions with one answer per row)
		 * Multiple choice - multiple answers:
		   - Checkboxes
		   - Checkbox matrix (group of questions with multiple answers per row)
		 * Single line text  (free text input box)
		 * Paragraph text (multiple line answer, used for longer responses)
		 * Date (for date type answers)
		 * File (for letting the respondents back their answers with additional information inside files)

		If you need to better describe certain sections of the survey, you can use the "Label" question, which has no answer. The respondent will only see the descriptive text.

		After adding a question, you can further customize it (e.g. set the available choices) by clicking on the corresponding "Edit" button, or you preview it by clicking on its title.

		To change the order of the questions, change the "sort order" column accordingly and press the "Set sort order" button.

				Radio buttons questions
				-----------------------

				Sometimes the choices of a radio question might not be enough for the respondent. In this case you can let the respondent answer with his own choice. To do this, go the the edit page of the question and set “Add extra option” to “Yes”.
				If the respondent chooses the extra option, the choice will appear exactly as he/she entered it in the survey answer and as “Other” in the reports.

				Changing questions after the survey was taken
				---------------------------------------------

				After the survey was taken, only a limited set of changes of the questions are permitted, e.g. the choices from multiple choice questions can't be changed. If no answer exists for a question, then the question can be changed in any way.
				To delete the existing answers enter the ZMI and delete all the “answer_*” objects.


		Reports
		-------

		To analyse the answers of the survey by aggregating them, you need to create one or more reports and add statistics (aggregations) to them.

		Click on the "Edit Reports" button to go to the reports management section. To add a new report, choose a title for it and click on "Add report". To change its description click on the corresponding "Edit" button. To configure the statistics included in the report, click on its title. Now choose the question that will be included in the report and then what kind of statistics would you like. There are 2 major types of statistics: numerical (tabular) and graphical (charts).

		Because adding a statistic one by one would take too much time for a complex survey with many questions, there is the possibility of creating a complete report with all the question - statistic combinations. To create this report, choose a title and click on the "Generate full report" button.


		Email notifications
		-------------------
		When a respondent answers, the owner of the survey can receive a notification email, which includes a link to the newly added answer. The notification can be enabled or disabled by using the "notify owner when someone takes the survey" setting.

		After a survey is taken the authenticated respondents can receive an email notification with their answer by using the "Email me my answer" setting. In some cases, e.g. short surveys, it is desirable to let administrators disable notifications, while in other cases, e.g. large surveys, notifications should always be sent. This is why, the survey has an "email answer to respondents" setting (for administrators) with the following choices:
		 * Always - a notification is always sent to respondents
		 * Never - a notification is never sent to respondents
		 * Let respondents choose (default is yes) - respondents can choose if they wish to receive a notification; the "Email me my answers" setting will be checked
		 * Let respondents choose (default is no) - respondents can choose if they wish to receive a notification; the "Email me my answers" setting will be unchecked 


Taking the survey
-----------------
Send the link of the survey to the respondents, so that they can take it. 

To prevent spam, captcha is used for anonymous users. Authenticated users are permitted to answer only once, but they can change their answers any time they wish too (if the survey has not expired).



Analysing the results
---------------------
The user managing the survey can see the individual answers by clicking on the "View answers" button from the survey's page and selecting the answer he/she wants to see.

While the individual answers can only be seen by a restricted group of users, the reports can be seen by anyone (if the default settings are used). To view the reports click on the "View reports" button from the survey's page and then select the report you want to see.



Administration
--------------

	Survey security model
	---------------------
	The following permissions exist:
	 * Add permissions:
	   - Naaya - Add Naaya Survey Tool: used for adding the survey tool
	   - Naaya - Add Naaya Survey Template; by default it's given to Manager and Administrator
	   - Naaya - Add Naaya Survey Report: used for reports; by default it's given to Manager and Administrator
	   - Naaya - Add Naaya Statistic: used for reports; by default it's given to Manager and Administrator
	   - Naaya - Add Naaya Survey Questionnaire: create a survey;  by default it's given to Contributor
	   - Naaya - Add Naaya Survey Attachment; by default it's given to Manager and Administrator'
	   - Naaya - Add Naaya Mega Survey: create a survey;  by default it's given to Contributor
	   - Naaya - Add Naaya Survey Answer: answer/take a survey; by default it's given to all users (Anonymous)
	* Edit/Manage permissions:
	   - Naaya - Manage Naaya Survey Template; by default it's given to Manager and Administrator
	   - the generic edit published object permission lets you edit Survey Questionnaires, Mega Surveys, questions and reports
	* View permissions:
	  - Naaya - View Naaya Survey Answers: view the list of answers; by default it's given to Contributor
	  - Naaya - View Naaya Survey Reports: view the reports;  by default it's given to all users (Authenticated and Anonymous)

	Also the Naaya - Add Naaya Widgets permission from NaayaWidgets is given by default to Manager and Administrator.

	When a Survey Tool is added, the security of the site will be configured as described above.
	Unsupported feature: the manage_configureSite method of portal_survey can also be called through the web.
