#include <stdio.h>
#include <dos.h>
#include <mem.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <jctype.h>

#define TEXT_SCORE "得点："
#define TEXT_GAME_OVER "ゲームオーバー"

#define FILE_SAVE "2048.sav"

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
#define BOARD_W 4
#define BOARD_H 4
#define BOARD_SIZE 16
typedef struct _game2048_t{
	unsigned short board[BOARD_H][BOARD_W];
	unsigned long score;
	unsigned char status;
}game2048_t;

/* Graphic functions */
union REGS inregs, outregs;
static uint16_t far* vram = 0xA0000000;
static uint16_t far* vramattr = 0xA0002000;

void clrscr();
void initscr(){
	putchar(0x1e);
	inregs.x.dx = 0;
	inregs.h.ah = 0x13;
	int86(0x18, &inregs, &outregs);
	outp(0x62, 0x4b);
	outp(0x60, 0x0f);
	inregs.h.ah=0x03;
	int86(0x18,&inregs,&outregs);
	clrscr();
}
void endscr(){
	clrscr();
	inregs.h.ah=0x03;
	int86(0x18,&inregs,&outregs);
	outp(0x62, 0x4b);
	outp(0x60, 0x8f);
	putchar(0x1e);
	printf("\033[2J");
}
void clrscr(){
	_fmemset((void far *)vram, 0, 4000);
	_fmemset((void far *)vramattr, 0, 4000);
}
void cputchar(uint16_t ch, uint16_t x, uint16_t y, uint16_t attr){
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	
	if (ch > 0xFF){
		*p_vram = ch - 0x20;
		*(p_vram + 1) = ch + 0x60;
		*(p_vramattr) = attr;
		*(p_vramattr + 1) = attr;
	} else {
		*p_vram = ch;
		*p_vramattr = attr;
	}
}
void cputstr(char* str, uint16_t x, uint16_t y, uint16_t attr){
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	char *ch;
				
	for (ch = str; *ch != '\0'; ch++){
		*p_vram = (uint16_t)(*ch);
		*p_vramattr = attr;
		p_vram++;
		p_vramattr++;
	}
}
void cputstrj(char* str, uint16_t x, uint16_t y, uint16_t attr){
	char *p;
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	uint16_t ch, ch2;
	for (p = str; *p != '\0'; p++, p_vram++, p_vramattr++){
		ch = 0xff&(*p); ch <<= 8; ch |= 0xff&(*(p+1));
		if (jiszen(ch)) {
			ch2 = jmstojis(ch);
			ch = (ch2 << 8) | (0xFF & (ch2 >> 8));
			*p_vram = ch - 0x20;
			*p_vramattr = attr;
			p++;
			p_vram++;
			p_vramattr++;
			*p_vram = ch + 0x60;
			*p_vramattr = attr;
		} else {
			*p_vram = (uint16_t)(*p);
			*p_vramattr = attr;
		}
	}
}
void drawframe(){
	int i;
	cputstrj(TEXT_SCORE, 28, 5, 0xc1);

#define ATTR_BORDER 0x21
	cputchar(0x9c, 27, 7, ATTR_BORDER);
	for (i = 0; i < 24; i++){
		cputchar(0x95, 28+i, 7, ATTR_BORDER);
	}
	cputchar(0x9d, 27+25, 7, ATTR_BORDER);

	for (i = 0; i < 9; i++){
		cputchar(0x96, 27, 8+i, ATTR_BORDER);
		cputchar(0x96, 27+25, 8+i, ATTR_BORDER);
	}

	cputchar(0x9e, 27, 17, ATTR_BORDER);
	for (i = 0; i < 24; i++){
		cputchar(0x95, 28+i, 17, ATTR_BORDER);
	}
	cputchar(0x9f, 27+25, 17, ATTR_BORDER);
}
void drawboard(game2048_t* game){
	int x, y;
	char buf[16] = {'\0'};
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (game->board[y][x]) {
				sprintf(buf, "%5u ", game->board[y][x]);
				cputstr(buf, 28+6*x, 9+(y<<1), 0xe1);
			} else {
				cputstr("    . ", 28+6*x, 9+(y<<1), 0xe1);
			}
		}
	}
	sprintf(buf, "%lu", game->score);
	cputstr(buf, 34, 5, 0xc1);
	if (game->status){
		cputstrj(TEXT_GAME_OVER, 33, 19, 0x43);
	}
}

/* Load and save */
int game2048_load(game2048_t* game, char* filename){
  int i;
  FILE *fp; uint16_t *p_board = game->board;
  fp = fopen(filename, "rb");
  if(NULL==fp){
    return 0;
  }
  fseek(fp,0,SEEK_SET);
  fread(game, sizeof(game2048_t), 1, fp);
  fclose(fp);
  return 1;
}
void game2048_save(game2048_t* game, char* filename){
  int i;
  FILE *fp; uint16_t *p_board = game->board;
  fp = fopen(filename, "wb");
  if(NULL==fp){
    return;
  }
  fseek(fp,0,SEEK_SET);
  fwrite(game, sizeof(game2048_t), 1, fp);
  fclose(fp);
}

/* Game functions */
int game2048_update(game2048_t* game);
void game2048_init(game2048_t* game){
	int i;
	uint16_t *p_board = game->board;
	srand(time(NULL));
	for (i = 0; i < BOARD_SIZE; i++, p_board++) {
		*p_board = 0;
	}
	game->score = 0;
	game->status = 0;
  if(!game2048_load(game, FILE_SAVE)){
	  game2048_update(game);
  }
}
void game2048_quit(game2048_t* game){
	if(0 == game->status){
    game2048_save(game, FILE_SAVE);
  }else{
    unlink(FILE_SAVE);
  }
}
int game2048_update(game2048_t* game){
	struct empty_space_t {
		int x;
		int y;
	} space[BOARD_SIZE];
	int space_len = 0, space_sel, x, y;
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (0 == game->board[y][x]){
				space[space_len].x = x;
				space[space_len].y = y;
				space_len++;
			}
		}
	}
	space_sel = rand() % space_len;
	x = space[space_sel].x;
	y = space[space_sel].y;
	game->board[y][x] = (rand() % 2) ? 2 : 4;
	if (space_len > 1){
		return 1;
	}
	
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (x < BOARD_W-1 && game->board[y][x] == game->board[y][x+1]){
				return 1;
			}
			if (y < BOARD_H-1 && game->board[y][x] == game->board[y+1][x]){
				return 1;
			}
		}
	}
	game->status = 2;
	return 2;
}
int game2048_move_up(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (x = 0; x < BOARD_W; x++){
		y0 = 0; y = 1;
		while (y < BOARD_H){
			if (0 == g->board[y0][x]){
				if (0 != g->board[y][x]){
					g->board[y0][x] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				y++;
			} else {
				if (0 == g->board[y][x]){
					y++;
				} else if (g->board[y0][x] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y0][x] <<= 1;
					g->board[y][x] = 0;
					y0++; y++;
					m = 1;
				} else {
					y0++;
					if (y0 == y) {
						y++;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_down(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (x = 0; x < BOARD_W; x++){
		y0 = BOARD_H - 1; y = BOARD_H - 2;
		while (y >= 0){
			if (0 == g->board[y0][x]){
				if (0 != g->board[y][x]){
					g->board[y0][x] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				y--;
			} else {
				if (0 == g->board[y][x]){
					y--;
				} else if (g->board[y0][x] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y0][x] <<= 1;
					g->board[y][x] = 0;
					y0--; y--;
					m = 1;
				} else {
					y0--;
					if (y0 == y) {
						y--;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_left(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (y = 0; y < BOARD_H; y++){
		x0 = 0; x = 1;
		while (x < BOARD_W){
			if (0 == g->board[y][x0]){
				if (0 != g->board[y][x]){
					g->board[y][x0] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				x++;
			} else {
				if (0 == g->board[y][x]){
					x++;
				} else if (g->board[y][x0] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y][x0] <<= 1;
					g->board[y][x] = 0;
					x0++; x++;
					m = 1;
				} else {
					x0++;
					if (x0 == x) {
						x++;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_right(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (y = 0; y < BOARD_H; y++){
		x0 = BOARD_W - 1; x = BOARD_W - 2;
		while (x >= 0){
			if (0 == g->board[y][x0]){
				if (0 != g->board[y][x]){
					g->board[y][x0] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				x--;
			} else {
				if (0 == g->board[y][x]){
					x--;
				} else if (g->board[y][x0] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y][x0] <<= 1;
					g->board[y][x] = 0;
					x0--; x--;
					m = 1;
				} else {
					x0--;
					if (x0 == x) {
						x--;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}

typedef enum _action_t{
	ACTION_NONE,
	ACTION_QUIT,
	ACTION_MOVE_UP,
	ACTION_MOVE_DOWN,
	ACTION_MOVE_LEFT,
	ACTION_MOVE_RIGHT,
}action_t;
action_t getaction(){
	unsigned int keycode;
	inregs.h.ah=0x05;
	int86(0x18,&inregs,&outregs);
	while(0==outregs.h.bh){
		asm hlt;
		inregs.h.ah=0x05;
		int86(0x18,&inregs,&outregs);
	}
	keycode=outregs.x.ax;
	switch (keycode){
		case 0x1b:
			return ACTION_QUIT;
		break;
		case 0x3a00:
			return ACTION_MOVE_UP;
		break;
		case 0x3d00:
			return ACTION_MOVE_DOWN;
		break;
		case 0x3b00:
			return ACTION_MOVE_LEFT;
		break;
		case 0x3c00:
			return ACTION_MOVE_RIGHT;
		break;
	}
}

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */
#define	BIOS_FLAG	*(unsigned char far *)0x00000501L	/* BIOS_FLAG at system area */
#define	SYSCLK_BIT	0x80		/* system clock bit  0:5/10/20MHz, 1:8/16MHz */
#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */
void main(){
  uint16_t counter;
	game2048_t game; int running = 1, moved;
	game2048_init(&game);

	initscr();
	drawframe();
	drawboard(&game);
	while (running && 0 == game.status){
		moved = 0;
		switch (getaction()){
			case ACTION_QUIT:
				running = 0;
			break;
			case ACTION_MOVE_UP:
				moved = game2048_move_up(&game);
			break;
			case ACTION_MOVE_DOWN:
				moved = game2048_move_down(&game);
			break;
			case ACTION_MOVE_LEFT:
				moved = game2048_move_left(&game);
			break;
			case ACTION_MOVE_RIGHT:
				moved = game2048_move_right(&game);
			break;
		}
		if (running && moved){
			drawboard(&game);
		}
	}
	if (game.status){
    if (BIOS_FLAG&SYSCLK_BIT){
      counter = 19968;
    } else {
      counter = 24576;
    }
    outp(TMRMODE, TMR1MOD3);
    outp(TMR1CLK, (int)(counter&0x00ff));
    outp(TMR1CLK, (int)(counter>>8));
	  outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));
		delay(100);
	  outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));
		while (ACTION_QUIT != getaction()){}
	}
	game2048_quit(&game);
	endscr();
}

