import flatland as fl


ReportSchema = fl.Dict.with_properties(widget="group") \
                      .of(

    fl.String.named('title') \
             .using(label=u"Title"),

)


SerisReviewSchema = fl.Dict.with_properties(widget="group") \
                           .of(

    fl.Integer.named('report_id'),

    fl.Dict.named('links') \
           .of(

        fl.Boolean.named('global'),

        fl.Boolean.named('european'),

        fl.Boolean.named('national'),

    )

)
