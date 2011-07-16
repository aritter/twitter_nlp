#include "labels.h"
#include <stdio.h>

int main(int argc, char **argv) {
  int d,k;
  int i,j;
  int **labels = load_labels(argv[1], &d, &k);

  for(i=0; i<d; i++) {
    for(j=0; j<k; j++) {
      printf("%d ", labels[i][j]);
    }
    printf("\n");
  }
}
