#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#ifdef _WIN32
#include <windows.h>
#endif

#define X 'X'
#define O 'O'
#define EMPTY ' '

char board[9];
char player, computer;

void clear() {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

void header() {
    printf("=== Terminal Tic-Tac-Toe ===\n\n");
}

void resetBoard() {
    for (int i = 0; i < 9; i++)
        board[i] = EMPTY;
}

void drawBoard() {
    printf(" %c | %c | %c \n", board[0], board[1], board[2]);
    printf("---+---+---\n");
    printf(" %c | %c | %c \n", board[3], board[4], board[5]);
    printf("---+---+---\n");
    printf(" %c | %c | %c \n\n", board[6], board[7], board[8]);
}

int checkWin() {
    int wins[8][3] = {
        {0,1,2},{3,4,5},{6,7,8},
        {0,3,6},{1,4,7},{2,5,8},
        {0,4,8},{2,4,6}
    };

    for (int i = 0; i < 8; i++) {
        if (board[wins[i][0]] != EMPTY &&
            board[wins[i][0]] == board[wins[i][1]] &&
            board[wins[i][0]] == board[wins[i][2]])
            return 1;
    }
    return 0;
}

int isDraw() {
    for (int i = 0; i < 9; i++)
        if (board[i] == EMPTY)
            return 0;
    return 1;
}

int freeSpaces() {
    int count = 0;
    for (int i = 0; i < 9; i++)
        if (board[i] == EMPTY)
            count++;
    return count;
}

void playerMove() {
    int move;
    do {
        printf("Enter position (1-9): ");
        scanf("%d", &move);
    } while (move < 1 || move > 9 || board[move - 1] != EMPTY);

    board[move - 1] = player;
}

void smartComputerMove() {
    int bestScore = -100, move = -1;

    for (int i = 0; i < 9; i++) {
        if (board[i] == EMPTY) {
            board[i] = computer;
            if (checkWin()) {
                move = i;
                board[i] = EMPTY;
                break;
            }
            board[i] = EMPTY;
        }
    }

    if (move == -1) {
        for (int i = 0; i < 9; i++) {
            if (board[i] == EMPTY) {
                board[i] = player;
                if (checkWin()) {
                    move = i;
                    board[i] = EMPTY;
                    break;
                }
                board[i] = EMPTY;
            }
        }
    }

    if (move == -1) {
        int choices[9], count = 0;
        for (int i = 0; i < 9; i++)
            if (board[i] == EMPTY)
                choices[count++] = i;
        move = choices[rand() % count];
    }

    board[move] = computer;
}

void announceWinner(char winner) {
    drawBoard();
    if (winner == player)
        printf(" You Win!\n");
    else
        printf(" Computer Wins!\n");
}

void twoPlayerWinner(char w) {
    drawBoard();
    printf(" Player %c Wins!\n", w);
}

int main() {
    srand(time(NULL));
    int mode;
    char playAgain;

    while (1) {
        clear();
        header();

        printf("Select mode:\n\n");
        printf(" 1) Single-player (vs Computer)\n");
        printf(" 2) Two-player (local)\n");
        printf(" 3) Exit\n\n");
        printf("Enter choice (1-3): ");
        scanf("%d", &mode);

        if (mode == 3) break;

        resetBoard();

        if (mode == 1) {
            clear();
            header();

            int c;
            printf("Choose your symbol:\n\n");
            printf(" 1) X (goes first)\n");
            printf(" 2) O\n\n");
            printf("Enter 1 or 2: ");
            scanf("%d", &c);

            player = (c == 1) ? X : O;
            computer = (player == X) ? O : X;

            char turn = X;

            while (1) {
                clear();
                header();
                drawBoard();

                if (turn == player) {
                    playerMove();
                } else {
                    printf("Computer is thinking...\n");
#ifdef _WIN32
                    Sleep(500);
#endif
                    smartComputerMove();
                }

                if (checkWin()) {
                    announceWinner(turn);
                    break;
                }

                if (isDraw()) {
                    drawBoard();
                    printf(" Match Draw!\n");
                    break;
                }

                turn = (turn == X) ? O : X;
            }

        } 
        else if (mode == 2) {
            char turn = X;

            while (1) {
                clear();
                header();
                drawBoard();
                printf("Player %c turn\n", turn);

                int move;
                do {
                    printf("Enter position (1-9): ");
                    scanf("%d", &move);
                } while (move < 1 || move > 9 || board[move - 1] != EMPTY);

                board[move - 1] = turn;

                if (checkWin()) {
                    twoPlayerWinner(turn);
                    break;
                }

                if (isDraw()) {
                    drawBoard();
                    printf(" Match Draw!\n");
                    break;
                }

                turn = (turn == X) ? O : X;
            }
        }

        printf("\nPlay again? (y/n): ");
        scanf(" %c", &playAgain);

        if (playAgain != 'y' && playAgain != 'Y')
            break;
    }

    return 0;
}
