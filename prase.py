import os
import re
#############################################################
#| Table Name | Engine | CharSet                  | Comment |
#| Param Name | Type   | IS NULL Or Default Value | COMMENT |
#|  ...       | ...    |  ...                     | ...     |
#| Primary Key| id     |  TYPE                    | ...     |
#| Key        | id     | index_name               | ...     |
#############################################################


def praseTableComment(line):
    pattern = re.compile("COMMENT='([^']*)'");
    line = line.replace(',',';');
    comment = pattern.findall(line);
    if len(comment) == 0:
        comment.append("");
    return comment[0];

def praseComment(line):
    pattern = re.compile("COMMENT\ '([^']*)'");
    line = line.replace(',',';');
    comment = pattern.findall(line);
    if len(comment) == 0:
        comment.append("");
    return comment[0];

def praseEngine(line):
    pattern = re.compile("ENGINE=([^\ ]*)\ ");
    Engine= pattern.findall(line);
    if len(Engine) == 0:
        Engine.append("");
    return Engine[0];

def praseCHARSET(line):
    pattern = re.compile("CHARSET=([^\ ]*)\ ");
    charSet= pattern.findall(line);
    if len(charSet) == 0:
        charSet.append("");
    return charSet[0];

def praseTableInfo(line,tableName):
    row = list();
    row.append(tableName);
    row.append(praseEngine(line));
    row.append(praseCHARSET(line));
    row.append(praseTableComment(line));
    return row;

def praseKeyInfo(line):
    row = list();
    #Primary Key
    if line.find("PRIMARY") != -1:
        pattern = re.compile("`([^`]*)`");
        primaryKey = pattern.findall(line);
        if len(primaryKey) > 0:            
            row.append(";".join(primaryKey));
            row.append(";".join(primaryKey));
            row.append("PRIMARY KEY");
            row.append(praseComment(line));
            
    else :
        pattern = re.compile("`([^`]*)`\ \(([^\)]*)");
        key_name = pattern.findall(line);
        if len(key_name) >= 1:
            pattern = re.compile("`([^`]*)`");
            key = pattern.findall(key_name[0][1]);
            row.append(key_name[0][0]);
            keys = ";".join(key);
            row.append(keys);
            row.append("KEY");
            row.append(praseComment(line));
    
    return row;

def praseAttr(line):
    row = list();
    
    # get attribute name
    pattern = re.compile("`([^`]*)`");
    attribute = pattern.findall(line)[0];
    row.append(attribute);
    
    # get attribute type
    pattern = re.compile("`\ ([^\ ]*)[\ ,]");
    attrType = pattern.findall(line)[0];
    row.append(attrType);
    
    default = "NOT SET";
    # get NULL or DEFAULT
    if line.find("DEFAULT NULL") != -1:
        default = "DEFAULT NULL";
    elif line.find("DEFAULT") != -1:
        #print line;
        pattern = re.compile("DEFAULT\ '([^']*)'");
        default = pattern.findall(line)[0];
    row.append(default);

    row.append(praseComment(line));
    return row;
    
        
    #print attrType;

def PraseCreateSql(sql, tableName):
    lines = sql.split('\n');
    #print "%35s"%tableName
    table = list();
    
    for line in lines:
        if len(line) <= 0:
            continue;
        if line.find("CREATE TABLE") != -1:
            continue;
        # engine
        if line.find("ENGINE") != -1:
            row = praseTableInfo(line, tableName);
            table.insert(0,row);
            continue;
        # index key
        if line.find("KEY") != -1:
            row = praseKeyInfo(line);
            table.append(row);
            continue;

        row = praseAttr(line);
        table.append(row);
    return table;


def writeFile(filename, table):
    f = open(filename,"w");
    for row in table:
        f.write(",".join(row)+"\n");
        #print row;
    f.close();


if __name__ == "__main__":
    f = open("product_db.sql");
    data = f.read();
    f.close();
    dblist = data.split(";\n");
    for txt in dblist:
        pattern = re.compile("CREATE TABLE `(.*)`");
        tableName = pattern.findall(txt);
        table = PraseCreateSql(txt, tableName[0]);
        writeFile("db/" + tableName[0] + ".csv", table);

