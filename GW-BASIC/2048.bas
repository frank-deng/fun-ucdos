10 CLS:RANDOMIZE TIMER:DEFINT A-Z
20 SC#=0:DIM B(4,4):DIM S(16,2):SL=0
40 LOCATE 8,8,0:PRINT STRING$(23,42);
50 FOR I=1 TO 9
60 LOCATE 8+I,8:PRINT "*";SPC(21);"*";
70 NEXT I
80 LOCATE 18,8:PRINT STRING$(23,42);
90 LOCATE 6,9:PRINT "Score:";
100 GOSUB 600:WHILE SL>0:K$=INPUT$(1)
110 IF K$=CHR$(27) THEN CLS:END ELSE IF K$="w" THEN GOSUB 200 ELSE IF K$="a" THEN GOSUB 300 ELSE IF K$="d" THEN GOSUB 400 ELSE IF K$="s" THEN GOSUB 500
120 WEND
130 LOCATE 20,15:PRINT "GAME OVER";
140 WHILE INPUT$(1)<>CHR$(27):WEND:CLS:END
200 M=0:FOR X=0 TO 3:Y0=0:Y=1:WHILE Y<=3
201 IF B(Y0,X)<>0 THEN GOTO 210
202 IF B(Y,X)<>0 THEN B(Y0,X)=B(Y,X):B(Y,X)=0:M=1
203 Y=Y+1:GOTO 290
210 IF B(Y,X)=0 THEN Y=Y+1:GOTO 290 ELSE IF B(Y0,X)=B(Y,X) THEN GOTO 220
211 Y0=Y0+1:IF Y0=Y THEN Y=Y+1
212 GOTO 290
220 SC#=SC#+B(Y,X):B(Y0,X)=B(Y0,X)*2:B(Y,X)=0:Y0=Y0+1:Y=Y+1:M=1
290 WEND:NEXT X:IF M=1 THEN GOSUB 600
299 RETURN
300 M=0:FOR Y=0 TO 3:X0=0:X=1:WHILE X<=3
301 IF B(Y,X0)<>0 THEN GOTO 310
302 IF B(Y,X)<>0 THEN B(Y,X0)=B(Y,X):B(Y,X)=0:M=1
303 X=X+1:GOTO 390
310 IF B(Y,X)=0 THEN X=X+1:GOTO 390 ELSE IF B(Y,X0)=B(Y,X) THEN GOTO 320
311 X0=X0+1:IF X0=X THEN X=X+1
312 GOTO 390
320 SC#=SC#+B(Y,X):B(Y,X0)=B(Y,X0)*2:B(Y,X)=0:X0=X0+1:X=X+1:M=1
390 WEND:NEXT Y:IF M=1 THEN GOSUB 600
399 RETURN
400 M=0:FOR Y=0 TO 3:X0=3:X=2:WHILE X>=0
401 IF B(Y,X0)<>0 THEN GOTO 410
402 IF B(Y,X)<>0 THEN B(Y,X0)=B(Y,X):B(Y,X)=0:M=1
403 X=X-1:GOTO 490
410 IF B(Y,X)=0 THEN X=X-1:GOTO 490 ELSE IF B(Y,X0)=B(Y,X) THEN GOTO 420
411 X0=X0-1:IF X0=X THEN X=X-1
412 GOTO 490
420 SC#=SC#+B(Y,X):B(Y,X0)=B(Y,X0)*2:B(Y,X)=0:X0=X0-1:X=X-1:M=1
490 WEND:NEXT Y:IF M=1 THEN GOSUB 600
499 RETURN
500 M=0:FOR X=0 TO 3:Y0=3:Y=2:WHILE Y>=0
502 IF B(Y0,X)<>0 THEN GOTO 510
503 IF B(Y,X)<>0 THEN B(Y0,X)=B(Y,X):B(Y,X)=0:M=1
504 Y=Y-1:GOTO 590
510 IF B(Y,X)=0 THEN Y=Y-1:GOTO 590 ELSE IF B(Y0,X)=B(Y,X) THEN GOTO 520
511 Y0=Y0-1:IF Y0=Y THEN Y=Y-1
512 GOTO 590
520 SC#=SC#+B(Y,X):B(Y0,X)=B(Y0,X)*2:B(Y,X)=0:Y0=Y0-1:Y=Y-1:M=1
590 WEND:NEXT X:IF M=1 THEN GOSUB 600
599 RETURN
600 SL=0:LOCATE 6,15:PRINT SC#;
610 FOR Y=0 TO 3:LOCATE (10+Y*2),9:FOR X=0 TO 3
620 IF B(Y,X)<>0 THEN PRINT USING "#####";B(Y,X); ELSE PRINT "    .";:S(SL,0)=Y:S(SL,1)=X:SL=SL+1
630 NEXT X:NEXT Y:IF SL=0 THEN RETURN
650 SE=INT(RND*20) MOD SL:Y=S(SE,0):X=S(SE,1):B(Y,X)=((INT(RND*10) MOD 2)+1)*2
660 LOCATE 10+2*Y,9+5*X:PRINT USING "#####";B(Y,X);:IF SL>1 THEN RETURN
670 FOR Y=0 TO 3:FOR X=0 TO 3
671 IF X<3 THEN IF B(Y,X)=B(Y,X+1) THEN RETURN
672 IF Y<3 THEN IF B(Y,X)=B(Y+1,X) THEN RETURN
680 NEXT X:NEXT Y:SL=0:RETURN
