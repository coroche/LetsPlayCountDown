import numpy as np
import operator
from sympy.utilities.iterables import multiset_permutations
from progress.bar import Bar
import itertools
import time
import datetime

#Numbers list
numbers=np.array([1,100,75,50],dtype='object')

#Target to hit
target=200

#dictionary of operators
ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,
}

def RPNSolver(expression):
	#solves a single RPN expression
	#copy of the expression that will be solved operator by operator
	e=np.copy(expression)
	solved=0	#flag to signify when all operations are complete
	Ans=None	#result of operations
	while solved==0:
		#find the first operator in the expression
		i=0
		while type(e[i]) is not str:
			i+=1
		
		#If the 1st operator is in the 2nd position take the first number as the (intermediate) solution
		if i==1:
			Ans=e[0]
		
		#If there are not enough operands for the operator return the current answer (if it is valid)
		#This will be an intermediate solution that doesn't use every number in the list
		if i<2:
			if Ans is None or Ans%1!=0 or Ans<0:
				return None
			else:
				return int(Ans)
		
		#check divide by zero
		if e[i]=='/' and e[i-1]==0:
			return None
		else:
			#operate on the two numbers infront of the operator
			Ans=ops[e[i]](e[i-2],e[i-1])
		#replace the two operands and the operator with the result of the operation
		e[i]=Ans
		e=np.delete(e,[i-1,i-2])

		#check if the whole expression has been solved
		if len(e)==1:
			solved=1
	
	#Check if the result exists, is an integer and is positive. If not return None.
	if Ans is None or Ans%1!=0 or Ans<0:
		return None
	else:
		return int(Ans)

def RPN_to_Infix(expression):
	#Converts an RPN expression to an infix expression with parenthesis
	e=expression.copy()
	solved=0
	infix='' #String to hold infox expression
	while solved==0:
		
		#find the first operator in expression
		i=0
		while not (type(e[i]) is str and len(e[i])==1): #operators are the only strings of length 1 in the list
			i+=1
		
		#intermediate solution
		if i==1:
			infix=str(e[0])
		if i<2:
			return infix
	
		#write the expression to a string with parenthesis (e[i-2] and e[i-2] may be expressions themselves)
		infix='('+str(e[i-2])+str(e[i])+str(e[i-1])+')'
		
		#replace the operands and operator with the new expression
		e[i]=infix
		e=np.delete(e,[i-1,i-2])
		
		#check if all operations have been completed
		if len(e)==1:
			solved=1
	
	#return the expression
	return infix



print()
print('numbers=',numbers)
print('target=',target)

tic=time.perf_counter()
operators=np.array(['+','-','/','*'],dtype='object')

N=len(numbers) #number of numbers in initial list

#Progress bar
bar = Bar('Carol Vordermaning...', max=(N+2)*(N+1)*N/6)

#Loop over all possible combinations of N-1 operators
for op in itertools.combinations_with_replacement(operators,N-1):
	bar.next()
	
	#Add combination of operators to numbers array
	expression=np.concatenate((numbers,op),dtype='object')
	
	#Loop over all permutations of expression array
	for p in itertools.permutations(expression):
		
		#skip expressions that begin with an operator
		if p[0] in operators:
			continue
		
		#convert the epression to an array and solve it
		p=np.array(p,dtype='object')
		Ans=RPNSolver(p)
		
		#if the target is hit create an return the infix expression. exit computation.
		if Ans==target:
			print()
			print('solution ',RPN_to_Infix(p))
			toc=time.perf_counter()
			print('execution time: ', toc-tic, 's')
			exit()
		
#if no solution is found
bar.finish()
print('No solution')
toc=time.perf_counter()
exetimestr = datetime.timedelta(seconds =toc-tic)
print('Execution time: ', exetimestr)