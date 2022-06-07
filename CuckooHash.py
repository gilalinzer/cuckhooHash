from BitHash import *
import pytest




class Node(object): # not accessed by client
    def __init__(self,key,data):
        self.key = key
        self.data = data
    
    def __str__(self):
        return "{" + str(self.key) + "," + str(self.data) + "}"

class CuckooHash(object):
    def __init__(self, size):
        # make two hash arrays in the size 
        self.__hashArray1 = [None] * (size)
        self.__hashArray2 = [None] * (size)
        self.__numKeys = 0 # will be updated in insert method 
        self.__size = size
    
    
    
    def insert(self,key,data): 
        
        
        # first do a find to make sure it's not there already 
        # and if it is there - return 
        
        if self.find(key): return False
        
        # if the insert will make the tables too big: grow
        
        # based on my tests to save the most memory 
        # we will do this when it's 80% full
        elif self.__numKeys > len(self.__hashArray1)*.8:
            self.__growHash()
        
        
        # insert using underlying eviction algorithm :
        if self.__insert(key,data): # if it is successful and returns true:
            self.__numKeys+=1   # increment num keys 
            return True    
        
        # since we limited the loop there might still be an evicted node
        # we can try to rehash and insert again 
        
        else: 
            self.reHash()
            if self.__insert(key,data):
                self.__numKeys+=1
                return True
        
        return False # if it still is failing 
   
    
    # this is the underlying algorithm cuckoo hash        
    def __insert(self,key,data):
        
        # create node to insert
        n = Node(key,data) 
        bucket1 = BitHash(key) % self.__size
        bucket2 = BitHash(key,2) % self.__size
        
        # we will start by inserting into the first array  
        CurBucket = bucket1
        CurArray = self.__hashArray1
        
        
        # limit the number of times we can attempt to evict
        for i in range(50):            
            # attempt to insert
            if not CurArray[CurBucket]: # if nothing is there currently
                CurArray[CurBucket] = n # put the node in the bucket
                return True # and return
               
            CurArray[CurBucket], n = n, CurArray[CurBucket] # switch node with item currently there 
           
            if CurBucket == bucket1: # if we are currently on the first table                            
                # rehash for the new evicted node  
                bucket1 = BitHash(n.key) % self.__size
                bucket2 = BitHash(n.key,2) % self.__size           
                CurBucket = bucket2 # we now move to second table                              
                CurArray = self.__hashArray2 
            
            else:  # we are on the second bucket                             
                bucket1 = BitHash(n.key) % self.__size
                bucket2 = BitHash(n.key,2) % self.__size            
                CurBucket = bucket1  # now move back to the first                         
                CurArray = self.__hashArray1                     
    
    # accessor method to use for testing
    def getNumKeys(self):
        return self.__numKeys
    
    # accessor method to use for testing
    def getLength(self):
        return len(self.__hashArray1)
        
    
    def reHash(self):
        # resets the bithash and reassigns the nodes to the proper buckets 
        # in the specfied two arrays
        
        ResetBitHash()
        
        # now move keys to proper buckets
        for i in range(len(self.__hashArray1)):
            n = self.__hashArray1[i]
            if n: # we need to use our insert method that accounts for collision
                self.__insert(n.key,n.data)
        
        for i in range(len(self.__hashArray2)):
            n = self.__hashArray2[i]
            if n:
                self.__insert(n.key,n.data)
                

    
    def __growHash(self): # doubles the size of the hash table
               
        
        # store our original arrays in temps
        temp1 = self.__hashArray1
        temp2 = self.__hashArray2
        
        # set our arrays to blank arrays double the size
        self.__hashArray1 = [None] * (len(self.__hashArray1)*2)
        self.__hashArray2 = [None] *(len(self.__hashArray2)*2) 
        
        # reset the size 
        self.__size*=2
        
        # as long as we are reasigning the buckets - reset the bit hash
        ResetBitHash()
        
        # now move keys from our temp arrays to proper buckets in the new arrays
        for i in range(len(temp1)):
            n = temp1[i]
            if n:
                self.__insert(n.key,n.data)
        
        for i in range(len(temp2)):
            n = temp2[i]
            if n:
                self.__insert(n.key,n.data)        
        
        
        
        
    # finds a certain node based on it's key and returns data 
    # if it's not there it returns None
    def find(self,key): 
        
        bucket1 = BitHash(key) % len(self.__hashArray1)
        bucket2 = BitHash(key,2) % len(self.__hashArray2)
        
        # two potential locations of the key
        opt1 = self.__hashArray1[bucket1]
        opt2 = self.__hashArray2[bucket2]
        
        for i in [opt1, opt2] :
            if i!=None and i.key==key: return i.data
        
        return False
    
    def delete(self,key):
        
        bucket1 = BitHash(key) % len(self.__hashArray1)
        bucket2 = BitHash(key,2) % len(self.__hashArray2)
        
        # two potential locations of the key
        opt1 = self.__hashArray1[bucket1]
        opt2 = self.__hashArray2[bucket2]
        
        for i in [opt1, opt2] : # reset that bucket to None
            if i!=None and i.key==key: 
                i = None 
                return True
        return False
        
        
    def __str__(self):
        array1 = "Hash Table 1: ("
        array2 = "Hash Table 2: ("
        for i in range(len(self.__hashArray1)):
            array1+=str(self.__hashArray1[i]) + " "
        array1+=")"
        
        for i in range(len(self.__hashArray2)):
            array2+=str(self.__hashArray2[i]) + " "
        array2+=")"   
        return array1+"\n"+array2
        



def main(): # used for multiple pytests
    h = CuckooHash(10)
    data =open("wordlist.txt")    # using word list with all unique words
    keys = []
    
    
    for i in range(100000):
        word = data.readline()
        h.insert(word,random.randint(1,100))        
        keys+=[word]    # also insert into an array so we can test 
    
    data.close() 
    return h,keys




# Torture test that does 100,000 inserts on a Cuckoo Hash object of size 10
# and makes sure all elements can be found in the Cuckoo Hash

def test_torture():
    # make sure all elements are there by looping through the array of the keys
    h,keys = main()
    
    for i in range(len(keys)):
        assert h.find(keys[i])!=False    
    
def test_length():    
    h = main()[0]
    # make sure the length of the array grew since we did so many inserts 
    assert h.getLength()!=10 # orginal length of each array was 100
    
def test_NumKeys():
    h = main()[0]
    # since this file has all unique words : there must have been 10,000
    # inserted words so lets test that num keys == 100,000
    
    assert h.getNumKeys() == 100000

# testing to make sure duplicate keys are not inserted
def test_no_dups():
    
    h = CuckooHash(10)
    # attempt to insert the same key 10 times
    for i in range(10):
        h.insert("test",1)
    assert h.getNumKeys() == 1
    
    # make sure the function returns false upon inserting a duplicate 
    assert h.insert("test",1) == False

# testing an empty cuckoo object
def test_empty():
    e = CuckooHash(10)
    assert e.getLength()==10
    assert e.getNumKeys()==0
    
    
        
    
    


pytest.main(["-v", "-s", "CuckooHash.py"])


