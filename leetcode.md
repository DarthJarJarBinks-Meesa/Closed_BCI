1/15/2026 - problem 1672
got a solution on my own:
    class Solution:
    def maximumWealth(self, accounts: List[List[int]]) -> int:
        wealth = 0
        for x in accounts:
            if sum(x) > wealth:
                wealth = sum(x)
        return wealth

chatgpt showed a way to do it in 1 line using the max function:
wealth = max(sum(x) for x in accounts)
OR can use the map function, which applies a function to all items in a list
return max(map(sum, accounts))

1/16/2026 - problem 412
got solution on my own:
    class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        answer = []
        for i in range(1,n+1): 
            if i % 5 ==0 and i % 3 ==0:
                answer.append("FizzBuzz") 
            elif i % 5 == 0:
                answer.append("Buzz")
            elif i % 3 == 0:
                answer.append("Fizz")
            else:
                answer.append(str(i))
        return answer

chatgpt didn't really have any notes
could have had an empty string and then add fizz if fivisible by three an buzz if divisible by 5 (less lines of code and allows room for additional ifs for other numbers)
***if s is an empty string, it returns a false value
    class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        answer = []
        for i in range(1,n+1): 
            s = ''
            if i % 3 == 0:
                s += 'Fizz'
            if i % 5 == 0:
                s += 'Buzz'
            answer.append(s or str(i))
        return answer


1/17 - problem 1342
got a solution on my own
class Solution:
    def numberOfSteps(self, num: int) -> int:
        count = 0
        while num != 0:
            if num % 2 == 0:
                num //= 2
            else:
                num -= 1
            count += 1
        return count

chat couldn't further optimize
space complexity is O(1); time complexity is O(log n)

Did another problem - 
was a lot harder than i thought; first into into linked lists and data structures
Linked Lists:
    - problem with arrays is that in order to remove/add items, you have to shift everything over (can be taxing)
    - linked lists can do it much easeir since you just remove the arrow connecting it to the prior item
    - singly linked lists can only go head to tail (front to back)
    - doubly linked lists can go both ways
    - can create pointers that iterate through linked lists at whatever speed you want:
        banana = linked list
            banana.next ##means you go to the next item
            banana.next.next ## means you jump to the second item
    if you return a linked list, it shows what has not been iterated through yet
my solution:
    # Definition for singly-linked list.
    # class ListNode:
    #     def __init__(self, val=0, next=None):
    #         self.val = val
    #         self.next = next
    class Solution:
        def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
            middle = end = head 
            while end and end.next:
                middle = middle.next
                end = end.next.next
            return middle 
space complexity is O(1), time complexity is O(n)

1/18/2026 - problem 383
got a solution on my own
class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        for letter in ransomNote: 
            if letter in magazine:
                magazine = magazine.replace(letter, '',1)
            else:
                return False
        return True
    time complexity O(n*m)
    space complexity O(m)
problem is that it created a lot of new strings
instead, can use Counter() function, which creates a dictionary counting how many times a character appears in a string
can then compare the values of each letter for Counter(ransomNote) and Counter(magazine)
if value from magazine is every bigger

    time complexity O(n+m)
    space complexity O(m) * m is max 26
    class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        ransom = Counter(ransomNote)
        mag = Counter(magazine)
        for letter in ransomNote:
            if ransom[letter] > mag[letter]:
                return False
        return True
i also did the probelm from yesterday and got it right for the most part (just forgat to put that mid = mid.next as i was just putting mid.next and not updating it)


