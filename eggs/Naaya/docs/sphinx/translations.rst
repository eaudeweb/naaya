Portal translations
===================

Translating messages with several versions in the target language
-----------------------------------------------------------------
If a message in english has several translations in the target language (ex. "type" in english can be translated by "Typ" and by "eingeben" in German, when it is used as a noun and as a verb, respectively), the two entries should receive both a message ID and a message value in the ZPT:

    <p i18n:translate="Type (translation tip: used as a noun)">Type</p>
    <p i18n:translate="Type (translation tip: used as a verb)">Type</p>

The value will be displayed in the english version and the ID will help the translater understand how he should... translate.