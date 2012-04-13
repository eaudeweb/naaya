import flatland as fl


ReportSchema = fl.Dict.of(

    fl.String.named('title') \
             .using(label=u"Title"),

)
