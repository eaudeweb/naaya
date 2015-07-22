default_email_templates = {

'instant': """\
<subject i18n:translate="">Change notification - <tal:block \
content="options/ob/title_or_id" i18n:name="title" /></subject>
<body_text i18n:translate="">
This is an automatically generated message to inform you that the item
"<tal:block content="options/ob/title_or_id" i18n:name="title" />" has been changed at
<tal:block content="options/ob/absolute_url" i18n:name="url" /> by
"<tal:block content="options/person" i18n:name="person" />".
</body_text>
""",

'daily': """\
<subject i18n:translate="">Changed items - daily digest</subject>
<body_text><tal:block i18n:translate="">
This is an automatically generated daily message listing modified items
in the "<tal:block content="options/portal" i18n:name="title" />" portal.</tal:block>
<tal:block repeat="item options/items" i18n:translate="">
<tal:block content="item/ob/title_or_id" i18n:name="title" /> \
(at <tal:block content="item/ob/absolute_url" i18n:name="url" />)
</tal:block>
</body_text>
""",

'weekly': """\
<subject i18n:translate="">Changed items - weekly digest</subject>
<body_text><tal:block i18n:translate="">
This is an automatically generated weekly message listing modified items
in the "<tal:block content="options/portal" i18n:name="title" />" portal.</tal:block>
<tal:block repeat="item options/items" i18n:translate="">
<tal:block content="item/ob/title_or_id" i18n:name="title" /> \
(at <tal:block content="item/ob/absolute_url" i18n:name="url" />)
</tal:block>
</body_text>
""",

'monthly': """\
<subject i18n:translate="">Changed items - monthly digest</subject>
<body_text><tal:block i18n:translate="">
This is an automatically generated monthly message listing modified items
in the "<tal:block content="options/portal" i18n:name="title" />" portal.</tal:block>
<tal:block repeat="item options/items" i18n:translate="">
<tal:block content="item/ob/title_or_id" i18n:name="title" /> \
(at <tal:block content="item/ob/absolute_url" i18n:name="url" />)
</tal:block>
</body_text>
""",

}
