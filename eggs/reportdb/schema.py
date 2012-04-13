import flatland as fl


ReportSchema = fl.Dict.of(

    fl.String.named('title') \
             .using(label=u"Title"),

)


SerisReviewSchema = fl.Dict.of(

    fl.Integer.named('report_id'),

    fl.Dict.named('links') \
           .of(

        fl.Boolean.named('global'),

        fl.Boolean.named('european'),

        fl.Boolean.named('national'),

    )

)
