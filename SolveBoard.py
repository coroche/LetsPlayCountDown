import itertools as it
import random

solutions=[] #List to store solutions as they're found

def solve_list(num_list,target,rpn):
	global solutions
	if target in num_list: #if the target is in the number list add it to solutions
		solutions.append([str(target)+' = '+str(target)])
	
	for pair in it.combinations(num_list, 2): #Loop through all pairs in the numbers list
		others=num_list.copy() 
		others.remove(pair[0])
		others.remove(pair[1]) #List of remaining numbers not in pair

		#Addition
		res=pair[0]+pair[1]
		new_rpn=rpn+[str(pair[0])+' + '+str(pair[1])+' = '+str(res)] #List of operations (equation strings) performed so far 
		if res==target: 
			#if the result of the operation equals the target write the operations to the solutions list
			solutions.append(new_rpn)
		else:
			#if not, create a new list with the result and remaining numbers and recurse
			new_list=[res]+others
			solve_list(new_list,target,new_rpn)

		#Multiplication
		if pair[0]!=1 and pair[1]!=1: #Optimisation: redundant to multiply by one
			res=pair[0]*pair[1]
			new_rpn=rpn+[str(pair[0])+' × '+str(pair[1])+' = '+str(res)]
			if res==target:
				solutions.append(new_rpn)
			else:
				new_list=[res]+others
				solve_list(new_list,target,new_rpn)

		#Subtraction
		#The operation that doesn't result in a negative number is chosen
		res=abs(pair[0]-pair[1])
		if pair[0]>pair[1]:
			new_rpn=rpn+[str(pair[0])+' - '+str(pair[1])+' = '+str(res)]
		else:
			new_rpn=rpn+[str(pair[1])+' - '+str(pair[0])+' = '+str(res)]
		if res==target:
			solutions.append(new_rpn)	
		else:
			new_list=[res]+others
			solve_list(new_list,target,new_rpn)

		#Division a/b
		if not pair[1] in [0,1]: #Cannot divide by 0, redundant to divide by 1
			res=pair[0]/pair[1]
			if res%1==0 and res!=pair[1]: #Check that the result of the operation is an integer (required by rules), check if a/b=b (redundant)
				res=int(res)
				new_rpn=rpn+[str(pair[0])+' ÷ '+str(pair[1])+' = '+str(res)]
				if res==target:
					solutions.append(new_rpn)
				else:
					new_list=[res]+others
					solve_list(new_list,target,new_rpn)

		#Division b/a
		if not pair[0] in [0,1]:
			res=pair[1]/pair[0]
			if res%1==0 and res!=pair[0]:
				res=int(res)
				new_rpn=rpn+[str(pair[1])+' ÷ '+str(pair[0])+' = '+str(res)]		
				if res==target:
					solutions.append(new_rpn)
				else:
					new_list=[res]+others
					solve_list(new_list,target,new_rpn)

	return None

def cleanSolutions(num_list,target):
	#Call solve_list and remove redundant and duplicate solutions
	global solutions
	solutions=[]
	solve_list(num_list,target,[])
	
	#Remove duplicates (same equations, just in a different order)
	dist_solutions=checkDup(solutions)
	
	#Remove redundant solutions (contains equation(s) that isn't used in hitting target
	dist_solutions=[i for i in dist_solutions if not checkRedund(i)]
	
	#Order solitions list by length so that the most efficient solutions are first
	dist_solutions.sort(key=len)
	
	solutions=[] #Clear original solutions list used for live solutions display
	return dist_solutions

def checkRedund(sol):
	#for each equation in a solution check that the result is used later in the solution
	#adds space before each equation so that searching ' ans ' will only search whole operands
	for i,eq in enumerate(sol[:-1]):
		ans=' '+eq[eq.find('=')+2:]+' '
		altEq=[' '+j for j in sol[i+1:]]
		ansUsed=[ans in j for j in altEq]
		if not True in ansUsed:
			return True
	return False

def checkDup(sols):
	#Takes each solution (minus the last equation that hits the target) and orders them alphabetically
	#We can then search for duplicates in this new list to find solutions that have all the same equations but might be in a different order
	solsSorted=[sorted(sol[:-1]) for sol in sols]
	isDuplicate=[sol in solsSorted[i+1:] for i,sol in enumerate(solsSorted)]
	distsols=[sol for i,sol in enumerate(sols) if not isDuplicate[i]]
	return distsols

#Used only for GUI
def currentSols():
	#used to fetch solutions (shortest first) live as they're added by solving thread
	if solutions:
		solutions.sort(key=len)
		return solutions
	else:
		return []