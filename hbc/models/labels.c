#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "labels.h"
#include "stats.h"

int *load_entity_map(char *fname, int D) {
  FILE *f;
  int *map;
  char *line = (char *) malloc (1024 * sizeof(char));
  int n;
  size_t nbytes = 1024 * sizeof(char);

  map = (int *) malloc (D * sizeof(int));

  /* No map? */
  if(strcmp(fname, "NONE") == 0) {
    for(n=0; n<D; n++) {
      map[n] = -1;
    }
    return map;
  }

  n = 0;
  f = fopen(fname, "r");
  while(getline(&line, &nbytes, f) != EOF) {
    line = strtok(line, "\n");
    map[n] = atoi(line);
    n += 1;
  }

  return map;
}

int **load_labels(char *fname, int *D, int *K) {
  FILE *f;
  int **labels;
  int n,m;
  char *line = (char *) malloc (1024 * sizeof(char));
  char *field;
  size_t nbytes;

  /* First pass, just figure out how much memory to allocate */
  n = 0;
  f = fopen(fname, "r");
  while(getline(&line, &nbytes, f) != EOF) {
    m = 0;
    line = strtok(line, "\n");
    field = strtok(line, " ");
    while(field != NULL) {
      field = strtok(NULL, " ");
      m += 1;
    }
    n += 1;
  }
  fclose(f);

  *D = n;
  *K = m;

  /* Second pass, allocate memory and read in values */
  labels = (int **) malloc (n * sizeof(int *));
  f = fopen(fname, "r");
  n = 0;
  while(getline(&line, &nbytes, f) != EOF) {
    m = 0;
    labels[n] = (int *) malloc (*K * sizeof(int));
    line = strtok(line, "\n");
    field = strtok(line, " ");
    while(field != NULL) {
      labels[n][m] = atoi(field);
      field = strtok(NULL, " ");
      m += 1;
    }
    n += 1;
  }
  fclose(f);
  
  return labels;
}

int **load_labels_s(char *input, int *D, int *K) {
  int **labels;
  int n,m;
  char *buffer = (char *) malloc (1024 * sizeof(char));
  char *line = (char *) malloc (1024 * sizeof(char));
  char *field;
  size_t nbytes;
  /* First pass, just figure out how much memory to allocate */
  n = 0;

  strcpy(buffer, input);
  line = strtok(buffer, "\n");
  do {
    m = 0;
    field = strtok(line, " ");
    while(field != NULL) {
      field = strtok(NULL, " ");
      m += 1;
    }
    n += 1;
  } while((line = strtok(NULL, "\n")) != NULL);

  *D = n;
  *K = m;

  /* Second pass, allocate memory and read in values */
  labels = (int **) malloc (n * sizeof(int *));
  n = 0;
  strcpy(buffer, input);
  line = strtok(buffer, "\n");
  do {
    m = 0;
    labels[n] = (int *) malloc (*K * sizeof(int));
    field = strtok(line, " ");
    while(field != NULL) {
      labels[n][m] = atoi(field);
      field = strtok(NULL, " ");
      m += 1;
    }
    n += 1;
  } while((line = strtok(NULL, "\n")) != NULL);

  free(buffer);
  free(line);
  
  return labels;
}

int sample_Mult_labeled(int w, double **post_beta, double* post_theta, int V, int K, double alpha, double eta, int *labels) {
  int    *labelIdx = (int    *) malloc (K * sizeof(int));
  double *post_z   = (double *) malloc ((K+1) * sizeof(double));
  int nLabels = 0;
  int i,j,z,result;

  j = 0;
  for(i=1; i<=K; i++) {
    if(labels[i-1]) {
      //printf("%d\n", i);
      labelIdx[j] = i;
      post_z[j]   = (ldf_Mult_smooth(0, eta, w, post_beta[i-1], 1, V)) + (ldf_Mult_smooth(0, alpha, i, post_theta, 1, K));
      //printf("%f\n", post_z[j]);
      j += 1;
    }
  }

  normalizeLog(post_z, 1, j);
  z = sample_Mult(post_z, 1, j);

  result = labelIdx[z-1];

  free(labelIdx);
  free(post_z);

  return result;
}

int sample_Mult_labeled_stop(int w, int s, double **post_beta, double* post_theta, int V, int K, double alpha, double eta, int *labels, int* labelIdx, double *post_z) {
  /* Faster to pass these? */
  //int    *labelIdx = (int    *) malloc (K * sizeof(int));
  //double *post_z   = (double *) malloc ((K+1) * sizeof(double));

  int nLabels = 0;
  int i,j,z,result;

  j = 0;
  for(i=1; i<=K; i++) {
    if(labels[i-1]) {
      labelIdx[j] = i;

      /* Is this word currently labeled as a "stopword"? */
      if(s == 1) {
        post_z[j] = (ldf_Mult_smooth(0, eta, w, post_beta[i-1], 1, V)) + (ldf_Mult_smooth(0, alpha, i, post_theta, 1, K));
      } else if(s == 2) {
        post_z[j] = (ldf_Mult_smooth(0, eta, w, post_beta[i-1], 1, V));
      } else {
	exit(1);
      }

      j += 1;
    }
  }

  normalizeLog(post_z, 1, j);
  z = sample_Mult(post_z, 1, j);

  result = labelIdx[z-1];

  //free(labelIdx);
  //free(post_z);

  return result;
}

void add_dst(double*dst, double*src, int hi) {
  int i;
  for (i=0; i<=hi; i++) { // <= because we copy the sum
    dst[i] += src[i];
  }
}
