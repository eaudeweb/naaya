def getUserWithUserid(auth_tool, userid):
        """
        Search for a user with the given ID, in this user folder and
        external sources. Returns None if user not found, or is anonymous.
        """
        if userid is None:
            return None

        if userid in auth_tool.user_names():
            return auth_tool.getUser(userid)

        for source in auth_tool.getSources():
            user_folder = source.getUserFolder()
            user = user_folder.getUser(userid)
            if user is not None:
                return user

        return None

def get_user_string(userid):
        auth_tool = context.getAuthenticationTool()
        user = getUserWithUserid(auth_tool, userid)
        return user.cn + ' (' + userid + ') - ' + user.mail

answers = context.getAnswers()
wk1, wk2 = [], []
for a in answers:
        value = a.getDatamodel().values()[0]
        user_string = get_user_string(a.respondent)
        if value == 0:
                wk1.append(user_string)
        if value == 1:
                wk2.append(user_string)

wk1.sort()
wk2.sort()

ret = [['Workgroup1', 'Workgroup2']]
for i in range(max(len(wk1), len(wk2))):
        s1, s2 = '', ''
        if len(wk1) > i:
                s1 = wk1[i]
        if len(wk2) > i:
                s2 = wk2[i]
        ret.append([s1, s2])

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/csv')
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=survey_report.csv')
return '\r\n'.join([','.join(r) for r in ret])

