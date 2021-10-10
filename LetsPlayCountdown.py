import tkinter as tk
from tkinter import ttk
import random, threading, time, pyglet, os
from PIL import Image, ImageTk
import SolveBoard


def newNumbers():
	#randomly generate new numbers list
	#create lists of all available number tiles and shuffle them
	large=list(range(25,101,25))
	small=list(range(1,11))*2
	random.shuffle(large)
	random.shuffle(small)

	#select tiles from the arrays based on input number of larges and concatenate
	largeCount=int(largeN.get())
	new_numbers=large[:largeCount]+small[:6-largeCount]

	#Populate numbers entry widgets
	for i in range(6):
		numbers[i].delete(0,'end')
		numbers[i].insert(0,new_numbers[i])
	return

def newTarget():
	#Randomly generate a new target number and write it to widget
	r=random.randint(100,999)
	target.delete(0,'end')
	target.insert(0,r)
	return

def solve():
	#Solve the current board
	#Pack and start progress bar to indicate computation in progress
	pb.pack(side='right')
	pb.start()
	
	#if the target or a number is missing generate new ones
	if not target.get():
		newTarget()
	for number in numbers:
		if not number.get():
			newNumbers()

	#clear calculation box and execuation time label
	calc.delete('1.0','end')
	exeTime_lbl.config(text='')

	#write number list widget values to list and target to integer
	num_list=[0]*6
	for i in range(6):
		num_list[i]=int(numbers[i].get())
	target_int=int(target.get())

	#Create and start a thread to solve the board
	t1=threading.Thread(target=solve_thread, args=(num_list,target_int), daemon=True)
	t1.start()

	#Monitor the progress of the computation
	monitor(t1,[])

def alt():
	#cycle through solutions
	global solNum
	solNum=(solNum+1)%len(solutions) #Loop back to solution 1 when end is reached

	#write new solution to calculation box
	writeSoltoCalc(solutions[solNum])

	#update status bar message to indicate which solution is currently displayed
	sols_lbl.config(text='Solution '+str(solNum+1)+' of '+str(len(solutions)))

	#first_btn is only available when not displaying the first solution
	if not solNum==0:
		enable([first_btn])
	else:
		disable([first_btn])
	return

def first():
	#display the first solution
	global solNum
	solNum=len(solutions)-1 #set current solution number to the last solution
	alt() #Loop back to the first solution and display it

def clear():
	#clear all solutions, target, numbers list, calculations and sataus bar displays
	global solutions
	solutions=[]

	for number in numbers:
		number.delete(0,'end')

	target.delete(0,'end')
	calc.delete('1.0','end')
	exeTime_lbl.config(text='')
	sols_lbl.config(text='')
	disable([alt_btn,first_btn])

def numVal(inStr,acttyp,digits,min,max):
	#validate that and entry to an entry box is numeric, of the right number of digits and between two limits
	if acttyp == '1': #insert
		if not inStr.isdigit():
			return False
		if len(inStr)>int(digits) or int(inStr)<int(min) or int(inStr)>int(max):
			return False
	return True

def disable(buttons):
	#disables all buttons in input list
	for button in buttons:
		button['state']='disabled'
		button['background'] = button.defaultBackground
	return

def enable(buttons):
	#enables all buttons in input list
	for button in buttons:
		button['state']='normal'
	return

def solve_thread(num_list,target):
	#called by thread to solve board
	global solutions,tic

	#disbale all buttons while solving board
	disable([new_num,new_trg,solve_btn,alt_btn,first_btn,clear])
	
	#record current time for execuation time calculation 
	tic=time.perf_counter()

	#solve board
	solutions=SolveBoard.cleanSolutions(num_list,target)
	
	return

def monitor(thread,currentSol):
	#continually moniters thread to update solutions count and display current shortest solution
	global toc,solNum

	if thread.is_alive():
		#if the thread is still active get list of solutions
		sols=SolveBoard.currentSols()
		if sols and (not currentSol or len(sols[0])<len(currentSol)):
			#if there is a shorter solution than what is currently displayed display the new one 
			currentSol=sols[0]
			writeSoltoCalc(currentSol)

		#update status bar with current number of solutions found
		sols_lbl.config(text=str(len(sols))+' solutions found')

		#wait 100ms and check again
		window.after(100, lambda: monitor(thread,currentSol))
	else:
		#if the thread has finished write final solutions to screen
		solNum=0

		#stop and hide the progress bar
		pb.stop() 
		pb.pack_forget()

		#write the shortest solution to the calulation box if one exists
		if len(solutions)==0:
			calc.insert('1.0','No solution')
		else:
			writeSoltoCalc(solutions[0])
			sols_lbl.config(text='Solution '+str(solNum+1)+' of '+str(len(solutions)))
		
		#Record current time and write total execution time to status bar
		toc=time.perf_counter()
		exeTime_lbl.config(text='Exe time: '+str(round(toc-tic,2))+'s')
		
		#Renable buttons (only enable alternative solution button if more than 1 solution exists)
		if len(solutions)>1:
			enable([alt_btn])
		enable([new_num,new_trg,solve_btn,clear])
	
def writeSoltoCalc(sol):
	#clear calculation box and write the input solution to it
	calc.delete('1.0','end')
	for steps in sol:
		calc.insert('end',steps+'\n')

def lCallback(l):
	#if a number is entered in the large spinbox write 6-l to the samll spinbox
	if l.get():
		small=6-int(l.get())
		smallN.delete(0,'end')
		smallN.insert(0,small)

def sCallback(s):
	#if a number is entered in the small spinbox write 6-s to the large spinbox
	if s.get():
		large=6-int(s.get())
		largeN.delete(0,'end')
		largeN.insert(0,large)	


class HoverButton(tk.Button):
	#new class of button that reacts to hovering
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"] #set defaultBackground attribute to current background
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

   	#if the curser enters the button area set background colour to avtivebackground
    def on_enter(self, e):
    	if self['state']=='normal':
        	self['background'] = self['activebackground']

    #if the curser leave the button area return to defaul background colour
    def on_leave(self, e):
    	if self['state']=='normal':
        	self['background'] = self.defaultBackground


#Configure window
window=tk.Tk()
window.title('Let\'s play Countdown!')
window.resizable(height=False,width=False)
window.configure(bg='#3b87c4')

#Create frames for main display and status bar for the bottom of the window 
main_fr=tk.Frame(window,bg='#4a6fb6')
main_fr.grid(row=0,column=0)
status_fr=tk.Frame(window,bg='#245b86')
status_fr.grid(row=1,column=0, sticky='ew')

#Split main display between board and side panel for buttons
board_fr=tk.Frame(main_fr,bg='#3b87c4')
board_fr.grid(row=0,column=0)
controls_fr=tk.Frame(master=main_fr,highlightbackground="black",highlightthickness=1,bg='#245b86')
controls_fr.grid(row=0,column=1,sticky='n',padx=10,pady=10)#(fill='both')

#Board Frame
#Banner
bannerWidth=200
bannerHeight=100
image1 = Image.open("banner.png").resize((bannerWidth, bannerHeight), Image.ANTIALIAS)
banner = ImageTk.PhotoImage(image1)
banner_lbl = tk.Label(board_fr,image=banner, width=bannerWidth, height=bannerHeight, bg='#3b87c4',padx=10,pady=10)
banner_lbl.pack()

#Frame each for target number, number list and calculation text box
target_fr=tk.Frame(master=board_fr,bg='#3b87c4')
target_fr.pack()
number_fr=tk.Frame(master=board_fr,bg='#3b87c4')
number_fr.pack()
calc_fr=tk.Frame(master=board_fr,height=500)
calc_fr.pack(fill='both',padx=10,pady=10)

#Target entry box, numeric entries between 0 and 999
target=tk.Entry(master=target_fr,width=3,justify='center',font=('Tw Cen MT Condensed Extra Bold', 32), validate="key", bg='#4a6fb6', fg='white')
target['validatecommand'] = (target.register(numVal),'%P','%d',3,0,999)
target.pack(padx=5,pady=5)

#Array of 6 entry boxes for number list
numbers=[]
for i in range(6):
	frame=tk.Frame(master=number_fr,borderwidth=1,bg='#3b87c4')
	frame.grid(row=0, column=i, padx=2, pady=2)

	en=tk.Entry(master=frame,width=3,justify='center',font=('Tw Cen MT Condensed Extra Bold', 24), validate="key", bg='#4a6fb6', fg='white')
	en['validatecommand'] = (en.register(numVal),'%P','%d',3,0,999)
	en.pack(padx=2, pady=2)
	numbers.append(en) #Save entry box to array for future reference

#Calculation text box
#Import font for calculation text box
pyglet.font.add_file('RockSalt-Regular.ttf')
#Add calculation text box
calc=tk.Text(master=calc_fr,height=5,width=25,font=('Rock Salt', 12), padx=25,pady=25)
calc.pack(fill='both')

#Control Frame
#Number list frame
num_ctrl_fr=tk.Frame(master=controls_fr, bg='#245b86')
num_ctrl_fr.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

#Target frame
target_ctrl_fr=tk.Frame(master=controls_fr)
target_ctrl_fr.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

#Solutions frame
solve_ctrl_fr=tk.Frame(master=controls_fr)
solve_ctrl_fr.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

#Clear button frame
clear_ctrl_fr=tk.Frame(master=controls_fr)
clear_ctrl_fr.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)

#Number list controls
#Large number selection
large_fr=tk.Frame(master=num_ctrl_fr, bg='#245b86')
large_fr.grid(row=0, column=0)
l = tk.StringVar()

#Small number selection
small_fr=tk.Frame(master=num_ctrl_fr, bg='#245b86')
small_fr.grid(row=1, column=0)
s = tk.StringVar()

#Larger numbers
label=tk.Label(master=large_fr, text='Large:', bg='#245b86', font=('Tw Cen MT Condensed Extra Bold', 12), fg='white')
label.grid(row=0, column=0)
largeN=tk.Spinbox(master=large_fr, from_=0, to=4, width=3,justify='center', textvariable=l,font=('Tw Cen MT Condensed Extra Bold', 12), validate="key", bg='#4a6fb6', fg='white', buttonbackground='#00b9af')
largeN['validatecommand'] = (largeN.register(numVal),'%P','%d', 1,0,4) #Number between 0 and 4
l.trace("w", lambda name, index,mode, var=l: lCallback(l)) #Callback to update s when l is changed
largeN.grid(row=0, column=1,pady=5)

#Small numbers
label=tk.Label(master=small_fr,text='Small:', bg='#245b86', font=('Tw Cen MT Condensed Extra Bold', 12), fg='white')
label.grid(row=0, column=0)
smallN=tk.Spinbox(master=small_fr, from_=2, to=6, width=3,justify='center', textvariable=s,font=('Tw Cen MT Condensed Extra Bold', 12), validate="key", bg='#4a6fb6', fg='white', buttonbackground='#00b9af')
smallN['validatecommand'] = (smallN.register(numVal),'%P','%d', 1,2,6) #Number between 2 and 6
s.trace("w", lambda name, index,mode, var=s: sCallback(s)) #Callback to update l when s is changed
smallN.grid(row=0, column=1,pady=5)

l.set(random.randint(0,4)) #Assign random numbers on startup

#Set uniform button colour and width 
btn_width=11
btn_col='#3b87c4'

#Generate new numbers
new_num=HoverButton(master=num_ctrl_fr,text='New Numbers',command=newNumbers,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', activebackground='#00b9af')
new_num.grid(row=2, column=0)

#Generate new target
new_trg=HoverButton(master=target_ctrl_fr,text='New Target',command=newTarget,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', activebackground='#00b9af')
new_trg.pack()

#Solve button
solve_btn=HoverButton(master=solve_ctrl_fr,text='Solve',  command=solve,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', activebackground='#00b9af')
solve_btn.pack()

#Alternative solution button
alt_btn=HoverButton(master=solve_ctrl_fr,text='Alt. Solution',  command=alt,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', state='disabled', activebackground='#00b9af')
alt_btn.pack()

#First solution button
first_btn=HoverButton(master=solve_ctrl_fr,text='First Solution',  command=first,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', state='disabled', activebackground='#00b9af')
first_btn.pack()

#Clear button
clear=HoverButton(master=clear_ctrl_fr,text='Clear',command=clear,width=btn_width, font=('Tw Cen MT Condensed Extra Bold', 12), bg=btn_col, fg='white', activebackground='#00b9af')
clear.pack()

#Status frame
#Progress bar
pb = ttk.Progressbar(status_fr,orient='horizontal',mode='indeterminate')

#Execution time label
exeTime_lbl=tk.Label(status_fr,text='',bg='#245b86',fg='white')
exeTime_lbl.pack(side='right')

#Solutions information label
sols_lbl=tk.Label(status_fr,text='',bg='#245b86',fg='white')
sols_lbl.pack(side='left')

window.mainloop()