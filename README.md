# Let's Play Countdown!
The purpose of this project is to solve the Countdown numbers game. Contestants must try to hit a target number by operating on a list of six numbers.

#### Number selection
Numbers are hidden on facedown tiles of two categories, large and small. There are 4 large number tiles (25, 50, 75, 100), and 20 small number tiles (1 to 10, two of each). One contestant chooses how many large numbers they want (between 0 and 4). The remaining positions are filled with small numbers. This makes a list of six numbers to use in trying to hit the target, a randomly generated number between 100 and 999.

#### Rules:
* Allowed operations are +, -, × and ÷  
* The result of each operation must be a non-negative integer  
* Each number in the list can only be used once  
* Not all numbers have to be used  
* 30 seconds are given to get as close to the target as possible
  
I will attempt to brute force all possible ways to operate on the initial numbers in order to hit the target number.

## Naive Approach

### Reverse Polish Notation
Reverse Polish Notation (or RPN) is an alternative notation for binary operations. With standard notation the operator is placed between the two operands (a + b). With RPN the operator follows the two operands (a b +). The advantage of using RPN is that the order of operation is defined without the need for parentheses. Looking at an example in standard notation, (a + b) * c, parentheses are needed to convey that a is added to be before the result is multiplied by c. In RPN this is written as a b + c *. We find the first operator in the expression and apply it to the two preceding operands. The next operator is then applied to the result and c. In order for an RPN expression to be valid every operator must be preceded by at least two more operands than operators. 

### Strategy
We can take advantage of this to solve the Countdown numbers game. If we create and array from the initial list of N numbers and N-1 operators, each permutation of this list will correspond to a different way of combining the operators and operands. Creating a different list for each combination of N-1 operators and solving for every permutation of these lists will yield every possible solution but at quite a large computational cost. Allowing for repetition, there are a total of (N+2)!/6 combinations of N-1 operators. Each of these lists will have (2N-1)! permutations so the total number of expressions to solve is (2N-1)!(N+2)!/6

|N|(2N-1)!(N+2)!/6|
|---|---|
|1|1|
|2|24|
|3|2400|
|4|604800|
|5|304819200|
|6|268240896000|

As we can see, the number of expressions gets a lot larger with every number we add to the initial list. It should be becoming obvious why this section is titled "Naive Approach"

### Implementation

The implementation of this approach can be seen in [rpnMethod.py](rpnMethod.py). As expected, this approach is quite slow. It takes roughly 3 hours to solve a 6 number board. A little bit over the 30s benchmark. As a lot of the expressions that are generated are not valid (an operator is left without enough operands) I thought I could speed this up by checking if each expression is valid before solving. This only slowed things down even further. Another approach is needed...

## Branching algorithm
The RPN permutation method has a lot of inefficiencies. The same series of operations are unnecessarily repeated many times, the commutativity of + and * isn't taken advantage of, computation time is wasted on invalid expressions, etc. Let's look at an example of these inefficiencies. In a game with 4 initial numbers the following expressions would be evaluated by the RPN method.

    (a+b)+c
    (b+a)+c
    c+(a+b)
    c+(b+a)
    (a+b)*c
    (b+a)*c
    c*(a+b)
    c*(b+a)
    (a+b)-c
    (b+a)-c
    c-(a+b)
    c-(b+a)
    (a+b)/c
    (b+a)/c
    c/(a+b)
    c/(b+a)

    
2 operators for each of the 16 expression means that 32 operations need to the done to evaluate these. We know that + and * are commutative and after performing the first evaluation we know the value of a+b so we don't need to repeat this. Let's store this is memory (x=a+b). We can then reduce these expressions to:

    x=a+b
    x+c
    x*c
    abs(x-c)
    x/c
    c/x
    
Only 6 operations are needed to do all the work that 32 did above. If x!=c then either x-c<0 or c-x<0. As the game rules don't allow negative values at any point in the calculation we take the absolute value of x-c so that only the valid option is considered. The reduction in operations is even greater for longer initial lists. When a+b is evaluated is then treated as being an initial number for another game, [(a+b),c]. This new list is then solved. To implement this method we will recursively pass the results of operations back into the solver to be evaluated with the remaining numbers.

#### Step 1
List all pairs that can be made from the initial list.

#### Step 2
Perform each of the 4 possible operations on each pair. Check if the result is the target. If there are remaining numbers go to step 3.

#### Step 3
Combine the result with the remaining numbers from the initial list to form a new list. Go back to step one with the new list.  
  
This method is also memory efficient as at any one time no more than N-2 new numbers are stored in memory.

### Example with a list of four numbers
![Tree](https://user-images.githubusercontent.com/49063400/135449050-67307fd8-a419-4ca2-8d43-9c93d6ac2f19.png)

## Implementation
The implementation of this method can be seen in [SolveBoard.py](SolveBoard.py). This method can run through all possible operations on a 6 number board in ~15s on my now 10 year old laptop. It will usually find a solution within the first second, so we're well within the time allocated on the game show. I then looked for ways to speed this up further. One possible bottleneck is all the concatenation and appending to the solutions list. When the list of operations for a solution the length of the list grows with each operation. Every time the target is hit the solution list grows by one. I tried initialising the solutions list as a large list of lists of length  (for 5 operations) and then removing the empty elements after the algorythm had finished. This had no consistent effect on the execution time and made the code less readable so so I reverted to the original.
