import ChartTool

def initialize(context):
    """ """
    context.registerClass(
        ChartTool.ChartTool,
        permission = 'Naaya - Add Naaya Chart Tool',
        constructors = (ChartTool.manage_addChartTool,),
        icon = 'www/ChartTool.png'
    )
