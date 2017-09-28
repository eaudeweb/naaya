The application manages registrations from anonymous users.

The information is saved and can be later reviewed by the original user based on an authentication consisting in the registration id and the user's last name. A confirmation mail is sent to the registering user and to a list of administrators.

The installation of the application can be done by:
1.	Copying the SemideRegistration folder (https://svn.eionet.europa.eu/repositories/Naaya/trunk/Naaya/SemideRegistration) in the Zope products folder (Naaya is a prerequisite)
2.	Creating a naaya folder
3.	Editing its subobjects to include Semide Registration

Portal administrators have the right to edit the meeting properties, view, edit and delete participants.

Registration information and future links can be edited in the Zope Page templates "registration_form" and "registration_press_form" in the ZMI under the application folder. In case mistakes are made, the default forms can be recalled at any time by clicking the "Reload registration forms" button.

The menu buttons can also be edited in the ZMI (ZPT "menu buttons" under the application folder).

IMPORTANT!!! Please be aware that using the "Reload registration forms" method overwrites ALL these three ZPTs: registration_form, registration_press_form and menu_buttons with the default hardcoded values.

Editing email templates is done similarly to the registration forms, within the folder email_templates located in the applicatio folder. Using the "Reload" tab-button overwrites all the zpt files within the current folder with the default hardcoded values.