import csv

def Append():
    csvf = open('CourseDetails.csv', mode='a', newline='')
    mywr = csv.writer(csvf, delimiter=',')
    CourseId = input("Enter Course ID: ")
    CourseName = input("Enter Course Name: ")
    Faculty = input("Enter Faculty Name: ")
    Fees = float(input("Enter Course Fees: "))
    mywr.writerow([CourseId, CourseName, Faculty, Fees])
    csvf.close()

def Read():
    with open('CourseDetails.csv', mode='r') as csvf:
        myrd = csv.reader(csvf, delimiter=',')
        nr = len(list(myrd))
        if nr == 0:
            print("No records in the file.")
        else:
            csvf.seek(0, 0)
            myrd = csv.reader(csvf, delimiter=',')
            for r in myrd:
                print("Course ID: ", r[0])
                print("Course Name: ", r[1])
                print("Faculty Name: ", r[2])
                print("Course Fees: ", r[3])

def Search(crid):
    found = False
    with open('CourseDetails.csv', mode='r') as csvf:
        myrd = csv.reader(csvf, delimiter=',')
        for r in myrd:
            if r[0] == crid:
                print(r)
                found = True
                break
    if not found:
        print("No such course in the file.")

def Update(cid):
    found = False
    csvf = open('CourseDetails.csv', mode='r+', newline='')
    temp = []
    myrd = csv.reader(csvf, delimiter=',')
    for r in myrd:
        if r[0] == cid:
            print("\n1. Course Name \n2. Faculty Name \n3. Fees")
            chupd = int(input("Enter your choice: "))
            if chupd == 1:
                Name = input("Enter Course Name: ")
                r[1] = Name
            elif chupd == 2:
                Faculty = input("Enter Faculty Name: ")
                r[2] = Faculty
            elif chupd == 3:
                Fees = float(input("Enter Course Fees: "))
                r[3] = Fees
            found = True
        temp.append(r)
    csvf.seek(0, 0)
    mywr = csv.writer(csvf, delimiter=',')
    mywr.writerows(temp)
    csvf.close()
    if found:
        print("Data updated successfully.")
    else:
        print("No such course in the file.")

def Delete(crd):
    found = False
    csvf = open('CourseDetails.csv', mode='r', newline='')
    temp = []
    myrd = csv.reader(csvf, delimiter=',')
    for r in myrd:
        if r[0] != crd:
            temp.append(r)
        else:
            found = True
    csvf.close()
    csvf = open('CourseDetails.csv', mode='w', newline='')
    mywr = csv.writer(csvf, delimiter=',')
    mywr.writerows(temp)
    csvf.close()
    if found:
        print("Data deleted successfully.")
    else:
        print("No such course in the file.")

ch = 0
print("\n1. Append \n2. Read \n3. Search \n4. Update \n5. Delete \n6. Exit")
while ch != 6:
    ch = int(input("Enter your choice: "))
    if ch == 1:
        Append()
    elif ch == 2:
        Read()
    elif ch == 3:
        crid = input("Enter Course ID to be searched: ")
        Search(crid)
    elif ch == 4:
        cid = input("Enter Course ID to be updated: ")
        Update(cid)
    elif ch == 5:
        crd = input("Enter Course ID to be deleted: ")
        Delete(crd)
    elif ch == 6:
        print("Thank you!")
    else:
        print("Enter a valid choice between 1 and 6.")
