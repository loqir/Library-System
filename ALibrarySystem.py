import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pymysql
from datetime import timedelta,date

LARGEFONT = ("Verdana", 35)

def acquire(accessionnumber,title,author1,author2,author3,isbn,publisher,publicationyear):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )
    
    cursor = connection.cursor()
    book = (accessionnumber,isbn)
    cursor.execute(f"INSERT INTO alibrarysystem.`book`\
(accessionnumber,isbn) VALUES {book}")
    
    cursor.execute(f"INSERT INTO alibrarysystem.`bookinformation`\
(isbn,title,publisher,publicationyear) select '{isbn}','{title}','{publisher}','{publicationyear}' \
where not exists (select isbn from bookinformation where isbn = '{isbn}')")
    
    cursor.execute(f"INSERT INTO author (isbn,author,author2,author3) \
select '{isbn}','{author1}','{author2}','{author3}' \
where not exists (select isbn from author where isbn = '{isbn}')")
    connection.commit()
    connection.close()

def withdraw(accessionNumber):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )

    cursor = connection.cursor()

    cursor.execute(f"DELETE FROM alibrarysystem.`book` WHERE AccessionNumber = '{accessionNumber}'")
    connection.commit()
    connection.close()

def create(memberid,name,faculty,phonenumber,email):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )

    cursor = connection.cursor()
    

    member = (memberid,name,faculty,phonenumber,email)
    finepayment = (memberid,)
    mysqlfinepayment = "INSERT INTO alibrarysystem.`finepayment` (membershipid) VALUES (%s)"
    cursor.execute(f"INSERT INTO alibrarysystem.`libmem` VALUES {member}")
    cursor.execute(mysqlfinepayment,finepayment)
    fine = (memberid,)
    mysqlfine = "INSERT INTO alibrarysystem.`fine` (membershipid) VALUES (%s)"
    cursor.execute(mysqlfine,fine)
    connection.commit()
    connection.close()


def check_exists(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    
    cursor.execute(f"select membershipid from libmem where membershipid = '{membershipid}'")
    return bool(cursor.fetchall())

def check_loans_or_fines(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"select membershipid from book inner join fine using (membershipid) where membershipid = '{membershipid}' and (paymentamount > 0  or borrowdate > returndate or (borrowdate is not null and returndate is null))")
    return bool(cursor.fetchall())

def get_details(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"SELECT * from libmem where membershipid = '{membershipid}'")
    return cursor.fetchall()



def delete(memberid):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )

    cursor = connection.cursor()

    cursor.execute(f"DELETE FROM alibrarysystem.`libmem` WHERE MembershipID = '{memberid}'")
    cursor.execute(f"DELETE FROM alibrarysystem.`finepayment` WHERE MembershipID = '{memberid}'")
    cursor.execute(f"DELETE FROM alibrarysystem.`fine` WHERE MembershipID = '{memberid}'")
    connection.commit()
    connection.close()


def update(memberid, name, faculty, phonenumber, email):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )

    cursor = connection.cursor()

    cursor.execute(f"update libmem set name = '{name}', faculty = '{faculty}', phonenumber = '{phonenumber}', email = '{email}' where membershipid = '{memberid}'")

    connection.commit()
    connection.close()

def borrow(membershipid,accessionnumber):
    connection = pymysql.connect(
        host='localhost',
        user='root', 
        password = "qalin123",
        db='alibrarysystem',
        )

    cursor = connection.cursor()
    cursor.execute(f"UPDATE alibrarysystem.`book` SET borrowdate = CAST(now() AS DATE), MembershipID = '{membershipid}', duedate = ADDDATE(CAST(now() as DATE) ,14) where \
((select reservedate from alibrarysystem.`bookreserve` where accessionnumber = '{accessionnumber}') is null or (select reservedate from alibrarysystem.`bookreserve` where \
accessionnumber = '{accessionnumber}' and membershipid = '{membershipid}') = (SELECT MIN(reservedate) FROM alibrarysystem.`bookreserve` where accessionnumber = '{accessionnumber}') and \
(returndate > borrowdate or borrowdate is null) and accessionnumber = '{accessionnumber}') and accessionnumber = '{accessionnumber}' and (select count(*) where membershipid = '{membershipid}') < 2 and \
(select paymentamount from alibrarysystem.`fine` where membershipid = '{membershipid}') = 0")
    cursor.execute(f"delete bookreserve from bookreserve INNER JOIN book using(accessionnumber) where bookreserve.membershipid = '{membershipid}' and accessionnumber = '{accessionnumber}'")
    connection.commit()
    connection.close()


def returnbook(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
        
    cursor = connection.cursor()
    cursor.execute(f"update book set returndate = cast(now() as date) where accessionnumber = '{accessionnumber}' and duedate <= cast(now() as date)")

    cursor.execute(f"update fine set paymentamount = paymentamount + (select datediff(cast(now() as date) ,(select duedate from book where accessionnumber = '{accessionnumber}'))) where \
membershipid = (select membershipid from book where accessionnumber = '{accessionnumber}')")

def reserve(membershipid,accessionnumber,reservedate):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"insert into bookreserve \
select '{accessionnumber}', '{membershipid}', '{reservedate}'\
where ((select count(*) from bookreserve where membershipid = '{membershipid}') <= 1 and (((select borrowdate from book where accessionnumber = '{accessionnumber}') is not null \
and ((select returndate from book where accessionnumber = '{accessionnumber}') is null)) or ((select returndate from book where accessionnumber = '{accessionnumber}')  < \
(select borrowdate from book where accessionnumber = '{accessionnumber}'))) and ((select paymentamount from fine where membershipid = '{membershipid}') = 0))")
    connection.commit()
    connection.close()



def cancelreservation(membershipid,accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"delete bookreserve from bookreserve inner join book \
using (accessionnumber) where (borrowdate > returndate or borrowdate < duedate) and \
accessionnumber = '{accessionnumber}' and bookreserve.membershipid = '{membershipid}'")
    connection.commit()
    connection.close()

def search(word,column):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"SELECT accessionnumber,title,author,author2,author3,isbn,\
publisher,publicationyear FROM bookinformation as t1 INNER JOIN author as t2 \
using (ISBN) INNER JOIN book as t3 using (ISBN) \
WHERE {column} = '{word}' OR {column} LIKE '% {word}' OR {column} LIKE '{word} %' \
OR {column} LIKE '% {word} %'")
    return cursor.fetchall()
    connection.commit()
    connection.close()



def payfine(membershipid,payment):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"update finepayment set paymentdate = CAST(now() as date) \
where (select paymentamount from fine where \
membershipid = '{membershipid}') = '{payment}' and membershipid = '{membershipid}'")
    cursor.execute(f"update fine set paymentamount = 0 \
where paymentamount = '{payment}' and membershipid = '{membershipid}'")
    connection.commit()
    connection.close()


def displayloanall():
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"SELECT accessionnumber,title,author,author2,author3,isbn,publisher,publicationyear \
FROM bookinformation as t1 INNER JOIN author as t2 using (ISBN) INNER JOIN \
book as t3 using (ISBN) where borrowdate < duedate or borrowdate > returndate \
or(borrowdate is not null and returndate is null)")
    return cursor.fetchall()
    connection.commit()
    connection.close()



def displayreserve():
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"SELECT accessionnumber,title,bookreserve.membershipid,name \
from libmem INNER JOIN bookreserve using(membershipid) INNER JOIN book \
using(accessionnumber) INNER JOIN bookinformation using (ISBN)")
    return cursor.fetchall()
    connection.commit()
    connection.close()
    


def displaymemberswithfine():
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()

    
    cursor.execute(f"SELECT membershipid,name,faculty,phonenumber,email \
from libmem INNER JOIN fine using (membershipid) where paymentamount > 0")
    return cursor.fetchall()
    connection.commit()
    connection.close()



def displayloan(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT accessionnumber,title,author,author2,author3,isbn,publisher,publicationyear \
from author INNER JOIN bookinformation using (ISBN) INNER JOIN book using (ISBN) \
where ((returndate is null and borrowdate is not null) or (borrowdate > returndate)) and membershipid = '{membershipid}'")
    return cursor.fetchall()
    connection.commit()
    connection.close()
    
class tkinterApp(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, Page1, Page2, MemberCreationPage, MemberDeletionPage, MemberUpdatePage,
                  Acquisition, Withdrawal, LoansMenu, BorrowPage, ReturnPage, Reservations, ReserveBook,
                  CancelReservation, Fines, Payment, Reports, Search, BooksOnLoan):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# first window frame startpage

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # label of frame Layout 2
        label = ttk.Label(self, text="A Library System", font=LARGEFONT)

        # putting the grid in its place by using
        # grid
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Membership",
                             command=lambda: controller.show_frame(Page1))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=4, padx=10, pady=10)

        ## button to show frame 2 with text layout2
        button2 = ttk.Button(self, text="Books",
                             command=lambda: controller.show_frame(Page2))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=4, padx=10, pady=10)

        ## button to show frame 3 with text layout3
        button3 = ttk.Button(self, text="Loans",
                             command=lambda: controller.show_frame(LoansMenu))

        # putting the button in its place by
        # using grid
        button3.grid(row=3, column=4, padx=10, pady=10)

        ## button to show frame 4 with text layout4
        button4 = ttk.Button(self, text="Reservations",
                             command=lambda: controller.show_frame(Reservations))

        # putting the button in its place by
        # using grid
        button4.grid(row=4, column=4, padx=10, pady=10)

        ## button to show frame 5 with text layout5
        button5 = ttk.Button(self, text="Fines",
                             command=lambda: controller.show_frame(Fines))

        # putting the button in its place by
        # using grid
        button5.grid(row=5, column=4, padx=10, pady=10)

        ## button to show frame 2 with text layout2
        button6 = ttk.Button(self, text="Reports",
                             command=lambda: controller.show_frame(Reports))

        # putting the button in its place by
        # using grid
        button6.grid(row=6, column=4, padx=10, pady=10)


# second window frame page1
class Page1(tk.Frame): #Membership

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="1. Creation",
                             command=lambda: controller.show_frame(MemberCreationPage))
        button1.grid(row=1, column=4, padx=10, pady=10)

        button2 = ttk.Button(self, text="2. Deletion",
                             command=lambda: controller.show_frame(MemberDeletionPage))
        button2.grid(row=2, column=4, padx=10, pady=10)

        button3 = ttk.Button(self, text="3. Update",
                             command=lambda: controller.show_frame(MemberUpdatePage))
        button3.grid(row=3, column=4, padx=10, pady=10)

        button4 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button4.grid(row=4, column=4, padx=10, pady=10)

class MemberCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Create Member, Please Enter Requested Information Below:")
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Membership Id ")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry (self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Name")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Faculty")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        label4 = ttk.Label(self, text="Phone Number")
        label4.grid(row=4, column=3, padx=10, pady=10)
        self.entry4 = tk.Entry(self)
        self.entry4.grid(row=4, column=4, padx=10, pady=10)

        label5 = ttk.Label(self, text="Email Address")
        label5.grid(row=5, column=3, padx=10, pady=10)
        self.entry5 = tk.Entry(self)
        self.entry5.grid(row=5, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Create Member",
                             command=lambda: self.create_member())
        button1.grid(row=6, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button2.grid(row=6, column=4, padx=10, pady=10)

    def create_member(self):
        try:
            create(self.entry1.get(), self.entry2.get(), self.entry3.get(), int(self.entry4.get()), self.entry5.get())
            tk.messagebox.showinfo(title="Success!", message="ALS membership created.")
        except Exception:
            tk.messagebox.showinfo(title="Error!", message="Member already exists; Missing or incomplete fields")

class MemberDeletionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Delete Member, Please Enter Membership ID:")
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Membership Id ")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Delete Member",
                             command=lambda: self.deletion_check())
        button1.grid(row=6, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Membership Menu",
                             command=lambda: controller.show_frame(Page1))
        button2.grid(row=6, column=4, padx=10, pady=10)

    def deletion_check(self):
        if (not check_exists(self.entry1.get())):
            tk.messagebox.showinfo(title="Error!", message="Member does not exist.")
            return

        if(check_loans_or_fines(self.entry1.get())):
            tk.messagebox.showinfo(title="Error!", message="Member has existing loans or fines")
            return
        else: 
            self.delete_confirmation(self.entry1.get())     


    def delete_confirmation(self, membershipID):
        member_id, name, faculty, phone_number, email = get_details(membershipID)[0]
        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Please confirm details to be correct").grid(row=0, column=4)

        label1 = ttk.Label(win, text="Membership Id ")
        label1.grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(win, text="name ")
        label2.grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=name).grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(win, text="faculty ")
        label3.grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=faculty).grid(row=3, column=4, padx=10, pady=10)

        label4 = ttk.Label(win, text="Phone number ")
        label4.grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=phone_number).grid(row=4, column=4, padx=10, pady=10)

        label5 = ttk.Label(win, text="email ")
        label5.grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text=email).grid(row=5, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Deletion", command=lambda: self.actual_delete(membershipID)).grid(row=6, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to delete function", command=lambda: win.destroy()).grid(row=6, column=4, padx=10, pady=10)

    def actual_delete(self, membershipID):
        tk.messagebox.showinfo(title = "Success!", message = "Member Deleted.")
        delete(membershipID)

    
class MemberUpdatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Update a Member, Please Enter Membership ID:")
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Membership Id ")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry (self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Name")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Faculty")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        label4 = ttk.Label(self, text="Phone Number")
        label4.grid(row=4, column=3, padx=10, pady=10)
        self.entry4 = tk.Entry(self)
        self.entry4.grid(row=4, column=4, padx=10, pady=10)

        label5 = ttk.Label(self, text="Email Address")
        label5.grid(row=5, column=3, padx=10, pady=10)
        self.entry5 = tk.Entry(self)
        self.entry5.grid(row=5, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Update Member",
                             command=lambda: self.popup())
        button1.grid(row=6, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Membership Menu",
                             command=lambda: controller.show_frame(Page1))
        button2.grid(row=6, column=4, padx=10, pady=10)

    def popup(self):
        inputs = (self.entry1, self.entry2, self.entry3, self.entry4, self.entry5)
        for i in inputs:
            if i.get() == "":
                tk.messagebox.showinfo(title="Error!", message="Missing or incomplete fields.")
                return
        win = tk.Toplevel()
        win.wm_title('test')
        ttk.Label(win, text="Please confirm details to be correct").grid(row=0, column=4)

        label1 = ttk.Label(win, text="Membership Id ")
        label1.grid(row=1, column=3, padx=10, pady=10)
        op1 = ttk.Label(win, text=self.entry1.get())
        op1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(win, text="Name")
        label2.grid(row=2, column=3, padx=10, pady=10)
        op2 = ttk.Label(win, text=self.entry2.get())
        op2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(win, text="Faculty")
        label3.grid(row=3, column=3, padx=10, pady=10)
        op3 = ttk.Label(win, text=self.entry3.get())
        op3.grid(row=3, column=4, padx=10, pady=10)

        label4 = ttk.Label(win, text="Phone Number")
        label4.grid(row=4, column=3, padx=10, pady=10)
        op4 = ttk.Label(win, text=self.entry4.get())
        op4.grid(row=4, column=4, padx=10, pady=10)

        label5 = ttk.Label(win, text="Email Address")
        label5.grid(row=5, column=3, padx=10, pady=10)
        op5 = ttk.Label(win, text=self.entry5.get())
        op5.grid(row=5, column=4, padx=10, pady=10)

        confirm_button = ttk.Button(win, text="Update Member", command=lambda: self.update_confirmation())
        confirm_button.grid(row=6, column=2, padx=1, pady=10)

        back_button = ttk.Button(win, text="Back to Membership menu", command=lambda: win.destroy())
        back_button.grid(row=6, column=4, padx=1, pady=10)

    def update_confirmation(self):
        if not check_exists(self.entry1.get()):
            tk.messagebox.showinfo(title="Error!", message="Member does not exist.")
            return
            
        update(self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry4.get(), self.entry5.get())
        tk.messagebox.showinfo(title="Success!", message="ALS membership Updated.")



# third window frame page2
class Page2(tk.Frame): #Books
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text="Acquisition",
                             command=lambda: controller.show_frame(Acquisition))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 3 with text
        # layout3
        button2 = ttk.Button(self, text="Withdrawal",
                             command=lambda: controller.show_frame(Withdrawal))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)

        button3 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button3.grid(row=3, column=1, padx=10, pady=10)

class Acquisition(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="For New Book Acquisition, Please Enter Required Information Below:")
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Title")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Author")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)
        
        label4 = ttk.Label(self, text="Author")
        label4.grid(row=4, column=3, padx=10, pady=10)
        self.entry4 = tk.Entry(self)
        self.entry4.grid(row=4, column=4, padx=10, pady=10)
        
        label5 = ttk.Label(self, text="Author")
        label5.grid(row=5, column=3, padx=10, pady=10)
        self.entry5 = tk.Entry(self)
        self.entry5.grid(row=5, column=4, padx=10, pady=10)

        label6 = ttk.Label(self, text="ISBN")
        label6.grid(row=6, column=3, padx=10, pady=10)
        self.entry6 = tk.Entry(self)
        self.entry6.grid(row=6, column=4, padx=10, pady=10)

        label7 = ttk.Label(self, text="Publisher")
        label7.grid(row=7, column=3, padx=10, pady=10)
        self.entry7 = tk.Entry(self)
        self.entry7.grid(row=7, column=4, padx=10, pady=10)

        label8 = ttk.Label(self, text="Publication Year")
        label8.grid(row=8, column=3, padx=10, pady=10)
        self.entry8 = tk.Entry(self)
        self.entry8.grid(row=8, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Add New Book",
                             command=lambda: self.add_book())
        button1.grid(row=9, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Books Menu",
                             command=lambda: controller.show_frame(Page2))
        button2.grid(row=9, column=4, padx=10, pady=10)
        
    def add_book(self):
        inputs = (self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry6.get(), self.entry7.get(), self.entry8.get())
        for i in inputs:
            if i =="":
                tk.messagebox.showinfo(title="Error!", message="Book already added, duplicate, missing or incomplete fields")
                return
        if BOOK_IN_LIB(self.entry1.get()):
            tk.messagebox.showinfo(title="Error!",
                                   message="Book already added, duplicate, missing or incomplete fields")
        if (not BOOK_IN_LIB(self.entry1.get())):
            acquire(self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry4.get(), self.entry5.get(), self.entry6.get(), self.entry7.get(), self.entry8.get())
            tk.messagebox.showinfo(title="Success!", message="New book added in library")

class Withdrawal(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Remove Outdated Books From System, Please Enter Required Information Below:")
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Withdraw Book",
                             command=lambda: self.withdraw_book(self.entry1.get()))
        button1.grid(row=2, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Books Menu",
                             command=lambda: controller.show_frame(Page2))
        button2.grid(row=2, column=4, padx=10, pady=10)

    def withdraw_book(self, accession_number):
        if (IS_ON_LOAN(self.entry1.get())):
            tk.messagebox.showinfo(title="Error!", message="Book on loan.")
        if (IS_RESERVED(self.entry1.get())):
            tk.messagebox.showinfo(title="Error!", message="Book currently reserved.")
        else:
            self.withdraw_confirmation(accession_number)

    def withdraw_confirmation(self, accession_number):
        access_number, title, author1, author2, author3, isbn, publisher, year = GET_BOOK_INFO(accession_number)[0]

        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Please confirm details to be correct").grid(row=0, column=4)

        ttk.Label(win, text="Accession Number ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=access_number).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Title ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=title).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text="Authors ").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=f"{author1} {author2} {author3}").grid(row=3, column=4, padx=10, pady=10)

        ttk.Label(win, text="ISBN ").grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=isbn).grid(row=4, column=4, padx=10, pady=10)
        ttk.Label(win, text="Publisher ").grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text=publisher).grid(row=5, column=4, padx=10, pady=10)

        ttk.Label(win, text="Year ").grid(row=6, column=3, padx=10, pady=10)
        ttk.Label(win, text=year).grid(row=6, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Withdrawal", command = lambda: self.actual_withdraw(accession_number)).grid(row=7, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to withdrawal function", command = lambda: win.destroy()).grid(row=7, column=4, padx=10, pady=10)

    def actual_withdraw(self, accession_number):
        tk.messagebox.showinfo(title ="Success!", message="Book withdrawn.")
        withdraw(accession_number)



class LoansMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="6. Borrow",
                             command=lambda: controller.show_frame(BorrowPage))
        button1.grid(row=1, column=4, padx=10, pady=10)

        button2 = ttk.Button(self, text="7. Return",
                             command=lambda: controller.show_frame(ReturnPage))
        button2.grid(row=2, column=4, padx=10, pady=10)

        button3 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button3.grid(row=3, column=4, padx=10, pady=10)

class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Borrow a Book, Please Enter Information Below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Membership ID")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Borrow Book",
                             command=lambda: self.borrow_check(self.entry1.get(), self.entry2.get()))
        button1.grid(row=3, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Loans Menu",
                             command=lambda: controller.show_frame(LoansMenu))
        button2.grid(row=3, column=4, padx=10, pady=10)

    def borrow_check(self, accession_number, member_id):
        if(IS_ON_LOAN(accession_number)):
            tk.messagebox.showinfo(title="Error!", message= f"Book currently on loan until: {GET_DUE_DATE(accession_number)}")
        elif(LOAN_QUOTA_EXCEEDED(member_id)):
            tk.messagebox.showinfo(title="Error!", message= "Member loan quota exceeded")
        elif(HAS_FINES(member_id)):
            tk.messagebox.showinfo(title="Error!", message="member has outstanding fines")
        elif not_reservation_priority(accession_number):
            tk.messagebox.showinfo(title="Error!", message="Other member has prior reservation")
        else:
            self.borrow_confirmation(accession_number, member_id)

    def borrow_confirmation(self, accession_number, member_id):
        access_number, title, author1, author2, author3, isbn, publisher, year = GET_BOOK_INFO(accession_number)[0]

        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Please confirm details to be correct").grid(row=0, column=4)

        ttk.Label(win, text="Accession Number ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=access_number).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Title ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=title).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text="Borrow Date ").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=date.today()).grid(row=3, column=4, padx=10, pady=10)

        ttk.Label(win, text="Membership ID ").grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=4, column=4, padx=10, pady=10)

        ttk.Label(win, text="Member Name ").grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text=GET_MEMBER_NAME(member_id)).grid(row=5, column=4, padx=10, pady=10)

        ttk.Label(win, text="Due date ").grid(row=6, column=3, padx=10, pady=10)
        ttk.Label(win, text= date.today() + timedelta(days = 14)).grid(row=6, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Loan", command=lambda: self.actual_borrow(member_id, accession_number)).grid(row=7, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to borrow function", command=lambda: win.destroy()).grid(row=7, column=4, padx=10, pady=10)

    def actual_borrow(self, member_id, accession_number):
        borrow(member_id,accession_number)
        tk.messagebox.showinfo(title ="Success!", message="Book borrowed.")


class ReturnPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Return a Book, Please Enter Information Below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Return Date (Today's Date)")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Return Book",
                             command=lambda: self.return_book(self.entry1.get()))
        button1.grid(row=3, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Loans Menu",
                             command=lambda: controller.show_frame(LoansMenu))
        button2.grid(row=3, column=4, padx=10, pady=10)

    def return_book(self, accession_number):
        access_number, title, author, author2, author3, isbn, publisher, year = GET_BOOK_INFO(accession_number)[0]
        member_id, member_name = GET_MEMBER_DEETS(accession_number)[0]
        fine = GET_FINE(accession_number)

        if not IS_ON_LOAN(accession_number):
            tk.messagebox.showinfo(title='Error!', message = 'Book not on loan.')
            return

        if BEFORE_DUE_DATE(accession_number):
            tk.messagebox.showinfo(title='Error!', message = 'Book not due yet.')
            return
        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Please confirm details to be correct").grid(row=0, column=4)

        ttk.Label(win, text="Accession Number ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=access_number).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Title ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=title).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text="Membership ID ").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=3, column=4, padx=10, pady=10)

        ttk.Label(win, text="Member Name ").grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_name).grid(row=4, column=4, padx=10, pady=10)

        ttk.Label(win, text="Return date ").grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text=self.entry2.get()).grid(row=5, column=4, padx=10, pady=10)

        ttk.Label(win, text="Fine ").grid(row=6, column=3, padx=10, pady=10)
        ttk.Label(win, text=f"${fine}").grid(row=6, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Return", command=lambda: self.return_confirmation(accession_number,return_date)).grid(row=7, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to return function", command=lambda: win.destroy()).grid(row=7, column=4, padx=10, pady=10)

    def return_confirmation(self, accession_number,returndate):
        tk.messagebox.showinfo(title='Success!', message = 'Book returned successfully')
        returnbook(accession_number,returndate)



class Reservations(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="8. Reserve a Book",
                             command=lambda: controller.show_frame(ReserveBook))
        button1.grid(row=1, column=4, padx=10, pady=10)

        button2 = ttk.Button(self, text="9. Cancel Reservation",
                             command=lambda: controller.show_frame(CancelReservation))
        button2.grid(row=2, column=4, padx=10, pady=10)

        button3 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button3.grid(row=3, column=4, padx=10, pady=10)

class ReserveBook(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Reserve a Book, Please Enter Information Below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Membership ID")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Reserve Date")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Reserve Book",
                             command=lambda: self.reserve_confirmation(self.entry1.get(), self.entry2.get(), self.entry3.get()))
        button1.grid(row=4, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Reservations Menu",
                             command=lambda: controller.show_frame(Reservations))
        button2.grid(row=4, column=4, padx=10, pady=10)

    def reserve_confirmation(self, accession_number, member_id, reservedate):
        if not IS_ON_LOAN(accession_number):
            tk.messagebox.showinfo(title = "Error!", message = "Book not currently on loan.")
            return
        if HAS_FINES(member_id):
            tk.messagebox.showinfo(title = "Error!", message = "Member has outstanding fine.") 
            return
        if RESERVE_QUOTA_EXCEEDED(member_id):
            tk.messagebox.showinfo(title = "Error!", message = "Member currently has 2 Books on reservation")
            return
        access_number, title, author1, author2, author3, isbn, publisher, year = GET_BOOK_INFO(accession_number)[0]
        member_id, name, faculty, phone_number, email = get_details(member_id)[0]

        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Confirm Reservation Details To Be Correct").grid(row=0, column=4)

        ttk.Label(win, text="Accession Number ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=access_number).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Book Title ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=title).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text="Membership ID ").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=3, column=4, padx=10, pady=10)

        ttk.Label(win, text="Member Name ").grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=name).grid(row=4, column=4, padx=10, pady=10)

        ttk.Label(win, text="Reserve date ").grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text= self.entry3.get()).grid(row=5, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Reservation", command= lambda : self.actual_reserve(member_id,accession_number,reservedate)).grid(row=6, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to Reserve Function", command= lambda : win.destroy()).grid(row=6, column=4, padx=10, pady=10)

    def actual_reserve(self, member_id, accession_number,reservedate):
        tk.messagebox.showinfo(title = "Success!", message = "Book successfully reserved")
        reserve(member_id, accession_number,reservedate)


class CancelReservation(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Cancel a Reservation, Please Enter Information Below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Accession Number")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Membership ID")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Cancel Date")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Cancel Reservation",
                             command=lambda: self.cancel_confirmation(self.entry1.get(), self.entry2.get(), self.entry3.get()))
        button1.grid(row=4, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Reservations Menu",
                             command=lambda: controller.show_frame(Reservations))
        button2.grid(row=4, column=4, padx=10, pady=10)

    def cancel_confirmation(self, accession_number, member_id, canceldate):
        if not IS_RESERVED_BY_MEMBER(accession_number, member_id):
            tk.messagebox.showinfo(title = "Error!", message = "Member has no such reservation.")
            return
        if not IS_RESERVED(accession_number):
            tk.messagebox.showinfo(title = "Error!", message = "This book is not reserved.")
            return
        
        access_number, title, author1, author2, author3, isbn, publisher, year = GET_BOOK_INFO(accession_number)[0]
        member_id, name, faculty, phone_number, email = get_details(member_id)[0]

        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Confirm Cancellation Details To Be Correct").grid(row=0, column=4)

        ttk.Label(win, text="Accession Number ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=access_number).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Book Title ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=title).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text="Membership ID ").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=3, column=4, padx=10, pady=10)

        ttk.Label(win, text="Member Name ").grid(row=4, column=3, padx=10, pady=10)
        ttk.Label(win, text=name).grid(row=4, column=4, padx=10, pady=10)

        ttk.Label(win, text="Cancellation date ").grid(row=5, column=3, padx=10, pady=10)
        ttk.Label(win, text= date.today()).grid(row=5, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Cancellation", command= lambda : self.actual_cancel(member_id, accession_number)).grid(row=6, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to Cancellation Function", command= lambda : win.destroy()).grid(row=6, column=4, padx=10, pady=10)

    def actual_cancel(self, member_id, accession_number):
        tk.messagebox.showinfo(title = "Success!", message = "Book successfully cancelled")
        cancelreservation(member_id, accession_number)
        
    

class Fines(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="10. Payment",
                             command=lambda: controller.show_frame(Payment))
        button1.grid(row=1, column=4, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button2.grid(row=3, column=4, padx=10, pady=10)

class Payment(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="To Pay a Fine, Please Enter Information Below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Membership ID")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Payment Date")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)

        label3 = ttk.Label(self, text="Payment Amount")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Pay Fine",
                             command=lambda: self.fine_confirmation(self.entry1.get(),self.entry2.get(),self.entry3.get()))
        button1.grid(row=4, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back To Fines Menu",
                             command=lambda: controller.show_frame(Fines))
        button2.grid(row=4, column=4, padx=10, pady=10)

    def fine_confirmation(self, member_id, paymentdate, paymentamount):
        if not HAS_FINES(member_id):
            tk.messagebox.showinfo(title = "Error!", message = "Member has no fine.")
            return
        if GET_PAYMENT_AMOUNT(member_id) != int(self.entry3.get()):
            tk.messagebox.showinfo(title = "Error!", message = "Incorrect fine payment amount.")
            return
        
        member_id, name, faculty, phone_number, email = get_details(member_id)[0]
        payment_amount = GET_PAYMENT_AMOUNT(member_id)

        win = tk.Toplevel()
        win.wm_title('Detail Confirmation')
        ttk.Label(win, text="Please Confirm Details To Be Correct").grid(row=0, column=4)

        ttk.Label(win, text="Member ID ").grid(row=1, column=3, padx=10, pady=10)
        ttk.Label(win, text=member_id).grid(row=1, column=4, padx=10, pady=10)

        ttk.Label(win, text="Payment Date ").grid(row=2, column=3, padx=10, pady=10)
        ttk.Label(win, text=self.entry2.get()).grid(row=2, column=4, padx=10, pady=10)

        ttk.Label(win, text=f"Payment Due: \nExact Fee Only").grid(row=3, column=3, padx=10, pady=10)
        ttk.Label(win, text= payment_amount).grid(row=3, column=4, padx=10, pady=10)

        ttk.Button(win, text="Confirm Payment", command= lambda : self.actual_pay(self.entry1.get(), self.entry3.get())).grid(row=4, column=3, padx=10, pady=10)
        ttk.Button(win, text="Back to Payment Function", command= lambda : win.destroy()).grid(row=4, column=4, padx=10, pady=10)

    def actual_pay(self, member_id, payment):
        tk.messagebox.showinfo(title = "Success!", message = "Fine successfully paid")
        payfine(member_id, payment)



class Reports(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Select one of the Options below", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="11. Book Search",
                             command=lambda: controller.show_frame(Search))
        button1.grid(row=1, column=4, padx=10, pady=10)

        button2 = ttk.Button(self, text="12. Books on Loan",
                             command=lambda: self.books_on_loan())
        button2.grid(row=2, column=4, padx=10, pady=10)

        button3 = ttk.Button(self, text="13. Books on Reservation",
                             command=lambda: self.books_on_reservation())
        button3.grid(row=3, column=4, padx=10, pady=10)

        button4 = ttk.Button(self, text="14. Outstanding Fines",
                             command=lambda: self.members_with_fines())
        button4.grid(row=4, column=4, padx=10, pady=10)

        button5 = ttk.Button(self, text="15. Books on Loan to Member",
                             command=lambda: controller.show_frame(BooksOnLoan))
        button5.grid(row=5, column=4, padx=10, pady=10)

        button6 = ttk.Button(self, text="Back To Main Menu",
                             command=lambda: controller.show_frame(StartPage))
        button6.grid(row=6, column=4, padx=10, pady=10)

    def books_on_loan(self):
        header = (("Accession number", "Title", "author1", "author2", 'author2', "ISBN", "Publisher", "Year"),)
        results = displayloanall()
        if len(results)<=0:
            tk.messagebox.showinfo(title='Error!', message = 'No books found!')
        table = header + results
        win = tk.Toplevel()
        for i in range(len(table)):
            for j in range(len(results[0])):
                tk.Label(win, text=table[i][j]).grid(row=i, column=j)
        tk.Button(win, text="Back to search function", command=lambda: win.destroy())

    def books_on_reservation(self):
        header = (("Accession number", "Title", "Member ID", "Name"),)
        results = displayreserve()
        if len(results)<=0:
            tk.messagebox.showinfo(title='Error!', message = 'No books found!')
            return
        table = header + results
        win = tk.Toplevel()
        for i in range(len(table)):
            for j in range(len(results[0])):
                tk.Label(win, text=table[i][j]).grid(row=i, column=j)
        tk.Button(win, text="Back to reports menu", command=lambda: win.destroy())

    def members_with_fines(self):
        header = (("Member ID", "Name", "Faculty", "Phone Number", "Email Address"),)
        results = displaymemberswithfine()
        if len(results)<=0:
            tk.messagebox.showinfo(title='Error!', message = 'No members found!')
            return
        table = header + results
        win = tk.Toplevel()
        for i in range(len(table)):
            for j in range(len(results[0])):
                tk.Label(win, text=table[i][j]).grid(row=i, column=j)
        tk.Button(win, text="Back to reports menu", command=lambda: win.destroy())
    
class Search(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Search based on one of the categories below:", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Title")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        label2 = ttk.Label(self, text="Authors")
        label2.grid(row=2, column=3, padx=10, pady=10)
        self.entry2 = tk.Entry(self)
        self.entry2.grid(row=2, column=4, padx=10, pady=10)
        
        label3 = ttk.Label(self, text="ISBN")
        label3.grid(row=3, column=3, padx=10, pady=10)
        self.entry3 = tk.Entry(self)
        self.entry3.grid(row=3, column=4, padx=10, pady=10)

        label4 = ttk.Label(self, text="Publisher")
        label4.grid(row=4, column=3, padx=10, pady=10)
        self.entry4 = tk.Entry(self)
        self.entry4.grid(row=4, column=4, padx=10, pady=10)

        label5 = ttk.Label(self, text="Publication Year")
        label5.grid(row=5, column=3, padx=10, pady=10)
        self.entry5 = tk.Entry(self)
        self.entry5.grid(row=5, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Search Book",
                             command=lambda: self.search())
        button1.grid(row=6, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Reports Menu",
                             command=lambda: controller.show_frame(Reports))
        button2.grid(row=6, column=4, padx=10, pady=10)

    def search(self):
        inputs = [self.entry1.get(), self.entry2.get(), self.entry3.get(), self.entry4.get(), self.entry5.get()]
        total = 0
        for i in inputs:
            total += bool(i)
        if total > 1:
            tk.messagebox.showinfo(title = 'Error!', message="Please only fill 1 field")
            return
        header = (("Accession number", "Title", "author1",'author2', 'author3', "ISBN", "Publisher", "Year"),)
        categories = ["Title", "author", "ISBN", "Publisher", "PublicationYear"]
        for i in range(len(inputs)):
            if inputs[i]:
                searchword = inputs[i]
                category = categories[i]
                hold = i
        results = search(searchword, category)
        if hold == 1:
            results += search(searchword, "author2")
            results += search(searchword, "author3")
        table = header + results
        
        if not results:
            tk.messagebox.showinfo(title = 'Error!', message="No info found")
            return
        win = tk.Toplevel()
        for i in range(len(table)):
            for j in range(len(results[0])):
                tk.Label(win, text=table[i][j]).grid(row=i, column=j)
        tk.Button(win, text="Back to search function", command=lambda: win.destroy())

class BooksOnLoan(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Books on Loan to Member", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        label1 = ttk.Label(self, text="Membership ID")
        label1.grid(row=1, column=3, padx=10, pady=10)
        self.entry1 = tk.Entry(self)
        self.entry1.grid(row=1, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Search Member",
                             command=lambda: self.get_books_on_loan())
        button1.grid(row=6, column=3, padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Reports Menu",
                             command=lambda: controller.show_frame(Reports))
        button2.grid(row=6, column=4, padx=10, pady=10)

    def get_books_on_loan(self):
        header = (("Accession number", "Title", "author1", "author2", 'author2', "ISBN", "Publisher", "Year"),)
        results = displayloan(self.entry1.get())
        if len(results)<=0:
            tk.messagebox.showinfo(title='Error!', message='No books found!')
            return
        table = header + results
        win = tk.Toplevel()
        for i in range(len(table)):
            for j in range(len(results[0])):
                tk.Label(win, text=table[i][j]).grid(row=i, column=j)
        tk.Button(win, text="Back to search function", command=lambda: win.destroy())







def IS_RESERVED(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select * from bookreserve where accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()

def IS_ON_LOAN(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )

    cursor = connection.cursor()
    cursor.execute(f"select membershipid from book \
where accessionnumber = '{accessionnumber}' and ((borrowdate > returndate) or \
(borrowdate is not null and returndate is null))")
    return cursor.fetchall()
    connection.commit()
    connection.close()


def BOOK_IN_LIB(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select *from book where accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()

def GET_BOOK_INFO(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT accessionnumber,title,author,author2,author3,isbn,publisher,publicationyear \
from book innner join bookinformation using (isbn) inner join author using (isbn) where accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()
    connection.commit()
    connection.close()

def LOAN_QUOTA_EXCEEDED(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select count(*) from book where membershipid = '{membershipid}' and ((borrowdate > returndate) or (borrowdate is not null and returndate is null))")
    return cursor.fetchall()[0][0] >=2

def RESERVE_QUOTA_EXCEEDED(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select COUNT(*) from bookreserve WHERE membershipid = '{membershipid}'")
    return cursor.fetchall()[0][0] >= 2 
    

def HAS_FINES(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select * from fine where membershipid = '{membershipid}' and paymentamount > 0")
    return cursor.fetchall()

def GET_MEMBER_NAME(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select name from libmem where membershipid = '{membershipid}'")
    return cursor.fetchall()[0][0]

def GET_DUE_DATE(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select duedate from book where accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()[0][0]

def IS_RESERVED_BY_MEMBER(accessionnumber,membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select * from bookreserve where membershipid = '{membershipid}' and accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()

def GET_PAYMENT_AMOUNT(membershipid):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select paymentamount from fine where membershipid = '{membershipid}'")
    return cursor.fetchall()[0][0]

def GET_MEMBER_DEETS(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select libmem.membershipid,name from book inner join libmem using (membershipid) where accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()


def GET_FINE(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select datediff (cast(now() as date), (select duedate from book where accessionnumber = '{accessionnumber}'))")
    return cursor.fetchall()[0]

def BEFORE_DUE_DATE(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select * from book where accessionnumber = '{accessionnumber}' and duedate > cast(now() as date)")
    return cursor.fetchall()


def not_reservation_priority(accessionnumber):
    connection = pymysql.connect(
    host='localhost',
    user='root', 
    password = "qalin123",
    db='alibrarysystem',
    )
    cursor = connection.cursor()
    cursor.execute(f"select * from bookreserve where reservedate != (SELECT MIN(reservedate) FROM alibrarysystem.`bookreserve` where accessionnumber = '{accessionnumber}') and accessionnumber = '{accessionnumber}'")
    return cursor.fetchall()
    
    

    
    
    
    
    
    

# Driver Code
app = tkinterApp()
app.geometry("800x500")
app.mainloop()



