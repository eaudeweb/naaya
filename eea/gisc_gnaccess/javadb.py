from contextlib import contextmanager

from jpype import java, JPackage, startJVM, shutdownJVM, getDefaultJVMPath

def config_directive(declaration):
    expect_names = ['db_user', 'db_password', 'java_classpath']
    declaration.expect(dict, names=expect_names)
    db_user = declaration.string('db_user', '')
    db_password = declaration.string('db_password', '')
    java_classpath = declaration.string('java_classpath', '')
    def callback():
        declaration.registry['db_user'] = db_user
        declaration.registry['db_password'] = db_password
        declaration.registry['java_classpath'] = java_classpath
    declaration.action(callback)

@contextmanager
def java_vm(context):
    class_path = context.registry['java_classpath']
    startJVM(getDefaultJVMPath(), '-ea', "-Djava.class.path=%s" % class_path)
    yield
    shutdownJVM()

def db_query_results(rs):
    while rs.next():
        count = rs.getMetaData().getColumnCount()
        yield [rs.getObject(i+1) for i in range(count)]

@contextmanager
def db_connection(context):
    JPackage('com.mckoi').JDBCDriver # force loading of JDBC driver
    db_user = context.registry['db_user']
    db_password = context.registry['db_password']
    connection = java.sql.DriverManager.getConnection(
                      "jdbc:mckoi://localhost/",
                      db_user, db_password)

    @contextmanager
    def db_statement(query):
        stmt = connection.createStatement()
        rs = stmt.executeQuery(query)
        yield db_query_results(rs)
        rs.close()
        stmt.close()

    yield db_statement

    connection.close()

def show_tables(db_statement):
    for line in db_statement("SHOW TABLES", db_statement):
        print line

def describe_table(name, db_statement):
    for line in db_statement("DESCRIBE %s" % name, db_statement):
        print line
