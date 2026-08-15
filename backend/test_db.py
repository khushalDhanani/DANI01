from app.db.mssql import execute_readonly_query
res = execute_readonly_query("SELECT PersonID, CreatedByUserID, PersonEntUser, PROwnerEmpID FROM DLPersonMst WHERE PersonID = 784252")
print("DLPersonMst:", res)
res2 = execute_readonly_query("SELECT * FROM ChangeContactOwnershipTransaction WHERE PersonID = 784252")
print("Transactions:", res2)
