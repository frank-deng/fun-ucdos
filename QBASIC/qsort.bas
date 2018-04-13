RANDOMIZE TIMER
DEFINT A-Z
DECLARE SUB QSORT(A() AS DOUBLE, L AS INTEGER, R AS INTEGER)
DECLARE SUB BSORT(A() AS DOUBLE, L AS INTEGER, R AS INTEGER)

DIM ARRAY(4096),ARRAY2(4096) AS DOUBLE
LENGTH = 666
FOR I = 0 TO LENGTH-1
  ARRAY(I) = RND * 100
  ARRAY2(I) = ARRAY(I)
NEXT I

T# = TIMER
CALL QSORT(ARRAY(), 0, LENGTH-1)
T_QSORT# = TIMER - T#
T# = TIMER
CALL BSORT(ARRAY2(), 0, LENGTH-1)
T_BSORT# = TIMER - T#

I = LENGTH - 1
IF ARRAY2(I) <> ARRAY2(I) THEN
  PRINT "Mismatch Detected"
END IF
FOR I = 0 TO LENGTH-2
  IF ARRAY(I) > ARRAY2(I+1) THEN
    PRINT "Quick Sort Failed"
    EXIT FOR
  END IF
  IF ARRAY2(I) > ARRAY2(I+1) THEN
    PRINT "Bubble Sort Failed"
    EXIT FOR
  END IF
  IF ARRAY2(I) <> ARRAY2(I) THEN
    PRINT "Mismatch Detected"
    EXIT FOR
  END IF
NEXT I

PRINT "Quick Sort Seconds: "; T_QSORT#
PRINT "Bubble Sort Seconds: "; T_BSORT#
END

SUB QSORT(A() AS DOUBLE, L AS INTEGER, R AS INTEGER)
  IF L >= R THEN EXIT SUB
  
  REM CHECK IF SEQ IS SORTED
  SORTED = 1
  FOR I = 0 TO R-1
    IF A(I) > A(I+1) THEN
      SORTED = 0
      EXIT FOR
    END IF
  NEXT I
  IF SORTED = 1 THEN EXIT SUB
  
  REM QUICK SORT MAIN
  I = L : J = R : K# = A(L)
  WHILE I < J
    WHILE I < J AND K# <= A(J)
      J = J - 1
    WEND
    A(I) = A(J)
    WHILE I < J AND K# >= A(I)
      I = I + 1
    WEND
    A(J) = A(I)
  WEND
  A(I) = K#
  
  REM QSORT FOR SUBGROUPS
  CALL QSORT(A(), L, I-1)
  CALL QSORT(A(), I+1, R)
END SUB

SUB BSORT(A() AS DOUBLE, L AS INTEGER, R AS INTEGER)
  FOR I=R TO L STEP -1:FOR J=L TO I-1
    IF A(J)>A(J+1) THEN
      T#=A(J):A(J)=A(J+1):A(J+1)=T#
    END IF
  NEXT J:NEXT I
END SUB