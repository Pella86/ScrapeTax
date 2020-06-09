#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 11:41:33 2020

@author: maurop
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May 18 20:44:22 2018
@author: Mauro
"""

#==============================================================================
# Matrix class
#   utilities for an nxm 2D matrix
#==============================================================================

# errors
class MatExcept(Exception):
    pass

# class
class Matrix:
    
    def __init__(self, m, n = None):
        # store matrix in a linear vector
        self.mat = []
        
        # if the first argument is a list and is a list of list
        # construct the matrix starting with that as an element
        if type(m) == list and type(m[0]) is list and n is None:
            self.m = len(m)
            self.n = len(m[0])
            
            self.init_mat()
            for i in range(self.m):
                for j in range(self.n):
                    self[i, j] = m[i][j]
        
        # if the first argument is a list, yet not a list of list
        # assume the user wants to create a mx1 vector
        elif type(m) is list and n is None:
            self.m = len(m)
            self.n = 1
            
            self.init_mat()
            for i in range(self.m):
                self[i, 0] = m[i]
                
        # else initialize a 0ed mxn matrix
        else:
            self.m = m
            self.n = n
            self.init_mat()

    def init_mat(self):
        for i in range(self.m):
            for j in range(self.n):
                self.mat.append(0)        
    
    # getter    
    def __getitem__(self, idx):
        linear_index = idx[1] * self.m + idx[0]      
        return self.mat[linear_index]
    
    # setter
    def __setitem__(self, idx, c):
        if idx[0] >= self.m or idx[0] < 0: raise MatExcept("Matrix: row out of range")
        if idx[1] >= self.n or idx[1] < 0: raise MatExcept("Matrix: col out of range")        
        
        linear_index = idx[1] * self.m + idx[0]
        self.mat[linear_index] = c
     
    # operator + elementwise sum
    def __add__(self, m2):
        if self.m == m2.m and self.n == m2.n:
            new_mat = []
            for i in range(len(self.mat)):
                new_mat.append(self.mat[i] + m2.mat[i])
            
            mnew = Matrix(self.m, self.n)
            mnew.mat = new_mat
            return mnew
            
        else:
            raise MatExcept("Matrix: addition not same size")
    
    # operator - element wise
    def __sub__(self, m2):
        if self.m == m2.m and self.n == m2.n:
            new_mat = []
            for i in range(len(self.mat)):
                new_mat.append(self.mat[i] - m2.mat[i])
            
            mnew = Matrix(self.m, self.n)
            mnew.mat = new_mat
            return mnew
            
        else:
            raise MatExcept("Matrix: subtraction not same size") 
    
    # matrix multiplication
    def __mul__(self, m2):
        if self.n == m2.m:
            mulmat = Matrix(self.m, m2.n)
            for i in range(mulmat.m):
                for j in range(mulmat.n):
                    for m in range(self.n):
                        mulmat[i, j] += self[i, m] * m2[m, j]
            return mulmat       
        else:
            raise MatExcept("Matrix: multiplication columns diff then rows")
    
    def scalar(self, k):
        mat_new = []
        for m in self.mat:
            mat_new.append(m * k)
        
        mres = Matrix(self.m, self.n)
        mres.mat = mat_new
        
        return mres
    
    def transpose(self):
        tmat = Matrix(self.n, self.m)
        
        for i in range(self.m):
            for j in range(self.n):
                tmat[j, i] = self[i, j]
        return tmat
            
    
    def __str__(self):
        s = ""
        for i in range(self.m):
            for j in range(self.n):
                
                s += str(self[i, j]) + " "
            s += "\n"
        
        return s
    
    
def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = Matrix(size_x, size_y)
    
    for x in range(size_x):
        matrix [x, 0] = x
        
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])


if __name__ == "__main__":
    print("--- init functions and assignment ----")
    
    m = Matrix(2, 3)
    print(m)
    
    m[1, 2] = 1
    print(m)
    
    m2 = Matrix(2, 3)
    m2[1, 2] = 3
    print(m2)
    print(m2.transpose())
    
    print(m + m2.scalar(4))
    
    print("--- mul ----")
    
    m1 = Matrix(2, 3)
    m1[0, 0] = 2
    m1[0, 1] = 3
    m1[0, 2] = 4
    m1[1, 0] = 1
    
    print(m1)
    
    m2 = Matrix(3, 2)
    m2[0, 1] = 1000
    m2[1, 0] = 1
    m2[1, 1] = 100
    m2[2, 1] = 10
    print(m2)
    
    print(m1 * m2)
    
    m1 = [ [1, 2],
           [3, 4] ]
    m1 = Matrix(m1)
    
    m2 = [ [0, 1],
           [0, 0] ]
    m2 = Matrix(m2)
    
    mres = m1 * m2
    print(mres)
    
    mres = m2 * m1
    print(mres)
    
    print ("--- list init ---")
    
    m = [ [2, 3, 4],
          [1, 0, 0] ]
    
    mini = Matrix(m)
    print(mini)
    
    
    print ("--- Levenshtein ---")
    
    v = levenshtein("helllo", "hello")
    print(v)
    