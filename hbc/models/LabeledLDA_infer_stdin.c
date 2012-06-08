/*
This program was automatically generated using:
     __  ____   ____
    / / / /  \ / __/  HBC: The Hierarchical Bayes Compiler
   / /_/ / / // /     http://hal3.name/HBC/
  / __  / --</ /      
 / / / / /  / /___    Version 0.7 beta
 \/ /_/____/\____/    

HBC is a freely available compiler for statistical models.  This generated
code can be built using the following command:

  gcc -O3 -lm labels.c stats.c samplib.c LabeledLDA_infer_stdin.c -o LabeledLDA_infer_stdin.out

The hierarchical model that this code reflects is:

alpha     ~ Gam(0.1,1)
eta       ~ Gam(0.1,1)
beta_{k}  ~ DirSym(eta, V)             , k \in [1,K]
theta_{d} ~ DirSym(alpha, K)           , d \in [1,D]
z_{d,n,m}   ~ Mult(theta_{d})          , d \in [1,D] , n \in [1,N_{d}] , m \in [1,M_{d,n}]
w_{d,n,m}   ~ Mult(beta_{z_{d,n,m}})   , d \in [1,D] , n \in [1,N_{d}] , m \in [1,M_{d,n}]

--# --define K 40
--# --loadD test w V D N M ;
--# --collapse beta
--# --collapse theta
--# --define alpha 0.1
--# --define eta 0.1
--# --dump best z
--# --niter 1000

Generated using the command:

  hbc compile LDA.hier LDA.c

Manually modified to handle inference using pre-computed topics (e.g. see Yao et. al 2009)
*/
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "stats.h"
#include "labels.h"

#define MAXLINE 8192

/**************************** SAMPLING ****************************/

void resample_post_beta(int D, int K, int** M, int* N, int V, double** post_beta, int*** w, int*** z) {
  int k_8;
  double* tmpSP4;
  int d_2;
  int n_74;
  int m_290;
  int dvv_loop_var_1;
  tmpSP4 = (double*) malloc(sizeof(double) * (1+((V) + (1))-(1)));
  for (k_8=1; k_8<=K; k_8++) {
    /* Implements direct sampling from the following distribution: */
    /*   Delta(post_beta_{k@8} | \sum_{d@2 \in [D]} \sum_{n@74 \in [N_{d@2}]} \sum_{m@290 \in [M_{d@2,n@74}]} .*(=(k@8, z_{d@2,n@74,m@290}), IDR(w_{d@2,n@74,m@290}, 1, V)), V) */
    for (dvv_loop_var_1=1; dvv_loop_var_1<=V; dvv_loop_var_1++) {
      tmpSP4[dvv_loop_var_1-1] = 0.0;
    }
    tmpSP4[(V) + (1)-1] = (0.0) * (((1) + (V)) - (1));
    for (d_2=1; d_2<=D; d_2++) {
      for (n_74=1; n_74<=N[d_2-1]; n_74++) {
        for (m_290=1; m_290<=M[d_2-1][n_74-1]; m_290++) {
          tmpSP4[(V) + (1)-1] += (1.0) * ((((k_8) == (z[d_2-1][n_74-1][m_290-1])) ? 1 : 0));
          tmpSP4[w[d_2-1][n_74-1][m_290-1]-1] += (1.0) * ((((k_8) == (z[d_2-1][n_74-1][m_290-1])) ? 1 : 0));
        }
      }
    }
    sample_Delta(post_beta[k_8-1], tmpSP4, V);
  }
  free(tmpSP4);
}

void resample_post_theta(int D, int K, int** M, int* N, double** post_theta, double** post_theta_train, double* global_topic_counts, int *entity_map, int*** z) {
  int d_9;
  double* tmpSP7;
  int n_3;
  int m_75;
  int dvv_loop_var_1;
  int i;
  tmpSP7 = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));
  for (d_9=1; d_9<=D; d_9++) {
    /* Implements direct sampling from the following distribution: */
    /*   Delta(post_theta_{d@9} | \sum_{n@3 \in [N_{d@9}]} \sum_{m@75 \in [M_{d@9,n@3}]} IDR(z_{d@9,n@3,m@75}, 1, K), K) */
    for (dvv_loop_var_1=1; dvv_loop_var_1<=K; dvv_loop_var_1++) {
      tmpSP7[dvv_loop_var_1-1] = 0.0;
    }
    tmpSP7[(K) + (1)-1] = (0.0) * (((1) + (K)) - (1));
    for (n_3=1; n_3<=N[d_9-1]; n_3++) {
      for (m_75=1; m_75<=M[d_9-1][n_3-1]; m_75++) {
        tmpSP7[(K) + (1)-1] += 1.0;
        tmpSP7[z[d_9-1][n_3-1][m_75-1]-1] += 1.0;
      }
    }
    if(entity_map == NULL) {
      sample_Delta(post_theta[d_9-1], tmpSP7, K);
    } else if (entity_map[d_9-1] == -1) {
      sample_Delta(post_theta[d_9-1], tmpSP7, K);
      add_dst(post_theta[d_9-1], global_topic_counts, K);
    } else {
      /*
      sample_Delta(post_theta[d_9-1], post_theta_train[entity_map[d_9-1]], K);
      for(i=0; i<=K; i++) {
        post_theta[d_9-1][i] /= post_theta[d_9-1][K];
        post_theta[d_9-1][i] *= 100.0;
      }
      add_dst(post_theta[d_9-1], tmpSP7, K);
      */
      add_dst(post_theta_train[entity_map[d_9-1]], tmpSP7, K);
    }
  }
  free(tmpSP7);
}

double resample_alpha(int D, int K, double alpha, double** post_theta) {
  double tmpSP0;
  int d_0;
  int cgds;
  /* Implements direct sampling from the following distribution: */
  /*   Gam(alpha | 0.1, /(1.0, -(1.0, /(1.0, \sum_{d@0 \in [D]} \sum_{cgds \in [K]} log(.*(/(1.0, sub(.+(alpha, post_theta_{d@0}), +(K, 1))), .+(alpha, post_theta_{d@0,cgds}))))))) */
  tmpSP0 = 0.0;
  for (d_0=1; d_0<=D; d_0++) {
    for (cgds=1; cgds<=K; cgds++) {
      tmpSP0 += log(((1.0) / ((alpha) + (post_theta[d_0-1][(K) + (1)-1]))) * ((alpha) + (post_theta[d_0-1][cgds-1])));
    }
  }
  alpha = sample_Gam(0.1, (1.0) / ((1.0) - ((1.0) / (tmpSP0))));
  return (alpha);
}

double resample_eta(int K, int V, double eta, double** post_beta) {
  double tmpSP2;
  int k_1;
  int cgds;
  /* Implements direct sampling from the following distribution: */
  /*   Gam(eta | 0.1, /(1.0, -(1.0, /(1.0, \sum_{k@1 \in [K]} \sum_{cgds \in [V]} log(.*(/(1.0, sub(.+(eta, post_beta_{k@1}), +(V, 1))), .+(eta, post_beta_{k@1,cgds}))))))) */
  tmpSP2 = 0.0;
  for (k_1=1; k_1<=K; k_1++) {
    for (cgds=1; cgds<=V; cgds++) {
      tmpSP2 += log(((1.0) / ((eta) + (post_beta[k_1-1][(V) + (1)-1]))) * ((eta) + (post_beta[k_1-1][cgds-1])));
    }
  }
  eta = sample_Gam(0.1, (1.0) / ((1.0) - ((1.0) / (tmpSP2))));
  return (eta);
}

void resample_z(int D, int** M, int* N, double alpha, double eta, double** post_beta, double** post_theta, double** post_theta_train, int* entity_map, int*** w, int*** z, int** labels, int K, int V) {
  int d_10;
  int n_16;
  int m_22;
  double* tmp_post_z_3;
  int tmp_idx_z_3;
  int dvv_loop_var_1;
  double *theta_counts;
  tmp_post_z_3 = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));
  for (d_10=1; d_10<=D; d_10++) {
    if(entity_map[d_10-1] == -1) {
      theta_counts = post_theta[d_10-1];
    } else {
      //theta_counts = post_theta[d_10-1];
      theta_counts = post_theta_train[entity_map[d_10-1]];
    }
    for (n_16=1; n_16<=N[d_10-1]; n_16++) {
      for (m_22=1; m_22<=M[d_10-1][n_16-1]; m_22++) {
        theta_counts[(K) + (1)-1] += (0.0) - (1.0);
        theta_counts[z[d_10-1][n_16-1][m_22-1]-1] += (0.0) - (1.0);
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][(V) + (1)-1] += (0.0) - ((1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0)));
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][w[d_10-1][n_16-1][m_22-1]-1] += (0.0) - ((1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0)));
        /* Implements multinomial sampling from the following distribution: */
        /*   (Mult(w_{d@10,n@16,m@22} | .+(eta, sub(post_beta, z_{d@10,n@16,m@22}))))(Mult(z_{d@10,n@16,m@22} | .+(alpha, post_theta_{d@10}))) */
        /***************************************************************
        for (dvv_loop_var_1=1; dvv_loop_var_1<=K; dvv_loop_var_1++) {
          tmp_post_z_3[dvv_loop_var_1-1] = 0.0;
        }
        tmp_post_z_3[(K) + (1)-1] = (0.0) * (((1) + (K)) - (1));
        for (tmp_idx_z_3=1; tmp_idx_z_3<=K; tmp_idx_z_3++) {
          tmp_post_z_3[tmp_idx_z_3-1] = (ldf_Mult_smooth(0, eta, w[d_10-1][n_16-1][m_22-1], post_beta[tmp_idx_z_3-1], 1, V)) + (ldf_Mult_smooth(0, alpha, tmp_idx_z_3, post_theta[d_10-1], 1, K));
        }
        normalizeLog(tmp_post_z_3, 1, K);
        z[d_10-1][n_16-1][m_22-1] = sample_Mult(tmp_post_z_3, 1, K);
        ***************************************************************/
        z[d_10-1][n_16-1][m_22-1] = sample_Mult_labeled(w[d_10-1][n_16-1][m_22-1], post_beta, theta_counts, V, K, alpha, eta, labels[d_10-1]);
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][(V) + (1)-1] += (1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0));
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][w[d_10-1][n_16-1][m_22-1]-1] += (1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0));
        theta_counts[(K) + (1)-1] += 1.0;
        theta_counts[z[d_10-1][n_16-1][m_22-1]-1] += 1.0;
      }
    }
  }
  free(tmp_post_z_3);
}

void resample_w(int D, int** M, int* N, double eta, double** post_beta, int*** w, int*** z, int V) {
  int d_11;
  int n_17;
  int m_23;
  for (d_11=1; d_11<=D; d_11++) {
    for (n_17=1; n_17<=N[d_11-1]; n_17++) {
      for (m_23=1; m_23<=M[d_11-1][n_17-1]; m_23++) {
        post_beta[z[d_11-1][n_17-1][m_23-1]-1][(V) + (1)-1] += (0.0) - ((1.0) * ((((z[d_11-1][n_17-1][m_23-1]) == (z[d_11-1][n_17-1][m_23-1])) ? 1 : 0)));
        post_beta[z[d_11-1][n_17-1][m_23-1]-1][w[d_11-1][n_17-1][m_23-1]-1] += (0.0) - ((1.0) * ((((z[d_11-1][n_17-1][m_23-1]) == (z[d_11-1][n_17-1][m_23-1])) ? 1 : 0)));
        /* Implements direct sampling from the following distribution: */
        /*   Mult(w_{d@11,n@17,m@23} | .+(eta, sub(post_beta, z_{d@11,n@17,m@23}))) */
        w[d_11-1][n_17-1][m_23-1] = sample_Mult_smooth(eta, post_beta[z[d_11-1][n_17-1][m_23-1]-1], 1, V);
        post_beta[z[d_11-1][n_17-1][m_23-1]-1][(V) + (1)-1] += (1.0) * ((((z[d_11-1][n_17-1][m_23-1]) == (z[d_11-1][n_17-1][m_23-1])) ? 1 : 0));
        post_beta[z[d_11-1][n_17-1][m_23-1]-1][w[d_11-1][n_17-1][m_23-1]-1] += (1.0) * ((((z[d_11-1][n_17-1][m_23-1]) == (z[d_11-1][n_17-1][m_23-1])) ? 1 : 0));
      }
    }
  }
}


/************************* INITIALIZATION *************************/

double initialize_alpha() {
  double alpha;
  alpha = sample_Gam(1.0, 1.0);
  return (alpha);
}

double initialize_eta() {
  double eta;
  eta = sample_Gam(1.0, 1.0);
  return (eta);
}

void initialize_z(int*** z, int D, int** M, int* N, int K) {
  int d_10;
  int n_16;
  int m_22;
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  int dvv_loop_var_3;
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=N[dvv_loop_var_1-1]; dvv_loop_var_2++) {
      for (dvv_loop_var_3=1; dvv_loop_var_3<=M[dvv_loop_var_1-1][dvv_loop_var_2-1]; dvv_loop_var_3++) {
        z[dvv_loop_var_1-1][dvv_loop_var_2-1][dvv_loop_var_3-1] = 0;
      }
      z[dvv_loop_var_1-1][dvv_loop_var_2-1][(M[dvv_loop_var_1-1][dvv_loop_var_2-1]) + (1)-1] = (0) * (((1) + (M[dvv_loop_var_1-1][dvv_loop_var_2-1])) - (1));
    }
  }
  for (d_10=1; d_10<=D; d_10++) {
    for (n_16=1; n_16<=N[d_10-1]; n_16++) {
      for (m_22=1; m_22<=M[d_10-1][n_16-1]; m_22++) {
        z[d_10-1][n_16-1][m_22-1] = sample_MultSym(1, K);
      }
    }
  }
}

void initialize_w(int*** w, int D, int** M, int* N, int V) {
  int d_11;
  int n_17;
  int m_23;
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  int dvv_loop_var_3;
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=N[dvv_loop_var_1-1]; dvv_loop_var_2++) {
      for (dvv_loop_var_3=1; dvv_loop_var_3<=M[dvv_loop_var_1-1][dvv_loop_var_2-1]; dvv_loop_var_3++) {
        w[dvv_loop_var_1-1][dvv_loop_var_2-1][dvv_loop_var_3-1] = 0;
      }
      w[dvv_loop_var_1-1][dvv_loop_var_2-1][(M[dvv_loop_var_1-1][dvv_loop_var_2-1]) + (1)-1] = (0) * (((1) + (M[dvv_loop_var_1-1][dvv_loop_var_2-1])) - (1));
    }
  }
  for (d_11=1; d_11<=D; d_11++) {
    for (n_17=1; n_17<=N[d_11-1]; n_17++) {
      for (m_23=1; m_23<=M[d_11-1][n_17-1]; m_23++) {
        w[d_11-1][n_17-1][m_23-1] = sample_MultSym(1, V);
      }
    }
  }
}

void initialize_post_beta(double** post_beta, int D, int K, int** M, int* N, int V, int*** w, int*** z) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  for (dvv_loop_var_1=1; dvv_loop_var_1<=K; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=V; dvv_loop_var_2++) {
      post_beta[dvv_loop_var_1-1][dvv_loop_var_2-1] = 0.0;
    }
    post_beta[dvv_loop_var_1-1][(V) + (1)-1] = (0.0) * (((1) + (V)) - (1));
  }
  resample_post_beta(D, K, M, N, V, post_beta, w, z);
}

void initialize_global_topic_counts(int ***z, double* global_topic_counts, int D, int K, int** M, int* N) {
  int i;
  int j;
  int k;

  /* Zero out counts */
  for(i=0; i<=K; i++) {
    global_topic_counts[i] = 0.0;
  }

  for(i=0; i<D; i++) {
    for(j=0; j<N[i]; j++) {
      for(k=0; k<M[i][j]; k++) {
        global_topic_counts[z[i][j][k]-1] += 1.0;
        global_topic_counts[K] += 1.0;        
      }
    }
  }

  /* Normalize */
  for(i=0; i<=K; i++) {
    global_topic_counts[i] /= global_topic_counts[K];
    //global_topic_counts[i] *= 100.0;
    global_topic_counts[i] *= 0.5;
  }
}

void initialize_post_theta(double** post_theta, double** post_theta_train, int *entity_map, double* global_topic_counts, int D, int K, int** M, int* N, int*** z) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=K; dvv_loop_var_2++) {
      post_theta[dvv_loop_var_1-1][dvv_loop_var_2-1] = 0.0;
    }
    post_theta[dvv_loop_var_1-1][(K) + (1)-1] = (0.0) * (((1) + (K)) - (1));
  }
  resample_post_theta(D, K, M, N, post_theta, post_theta_train, global_topic_counts, entity_map, z);
}


/**************************** DUMPING *****************************/

void dump_alpha(double alpha) {
  printf("alpha = ");
  printf("%g", alpha);
  printf("\n"); fflush(stdout);
}

void dump_eta(double eta) {
  printf("eta = ");
  printf("%g", eta);
  printf("\n"); fflush(stdout);
}

void dump_beta(int K, int V, double** beta) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  printf("beta = ");
  for (dvv_loop_var_1=1; dvv_loop_var_1<=K; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=V; dvv_loop_var_2++) {
      printf("%g", beta[dvv_loop_var_1-1][dvv_loop_var_2-1]);
      printf(" ");
    }
    printf(" ; ");
  }
  printf("\n"); fflush(stdout);
}

void dump_theta(int D, int K, double** theta) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  printf("theta = ");
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=K; dvv_loop_var_2++) {
      printf("%g", theta[dvv_loop_var_1-1][dvv_loop_var_2-1]);
      printf(" ");
    }
    printf(" ; ");
  }
  printf("\n"); fflush(stdout);
}

void dump_z(int D, int** M, int* N, int*** z) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  int dvv_loop_var_3;
  printf("z = ");
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=N[dvv_loop_var_1-1]; dvv_loop_var_2++) {
      for (dvv_loop_var_3=1; dvv_loop_var_3<=M[dvv_loop_var_1-1][dvv_loop_var_2-1]; dvv_loop_var_3++) {
        printf("%d", z[dvv_loop_var_1-1][dvv_loop_var_2-1][dvv_loop_var_3-1]);
        printf(" ");
      }
      printf(" ; ");
    }
    printf(" ;; ");
  }
  printf("\n"); fflush(stdout);
}

void dump_w(int D, int** M, int* N, int*** w) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  int dvv_loop_var_3;
  printf("w = ");
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=N[dvv_loop_var_1-1]; dvv_loop_var_2++) {
      for (dvv_loop_var_3=1; dvv_loop_var_3<=M[dvv_loop_var_1-1][dvv_loop_var_2-1]; dvv_loop_var_3++) {
        printf("%d", w[dvv_loop_var_1-1][dvv_loop_var_2-1][dvv_loop_var_3-1]);
        printf(" ");
      }
      printf(" ; ");
    }
    printf(" ;; ");
  }
  printf("\n"); fflush(stdout);
}


/*************************** LIKELIHOOD ***************************/

double compute_log_posterior(int D, int K, int** M, int* N, int V, double alpha, double** beta, double eta, double** theta, double** theta_train, int* entity_map, int*** w, int*** z) {
  double ldfP4_0;
  double ldfP4_1;
  double ldfP4_2;
  int m_22;
  int n_16;
  int d_10;
  double ldfP5_0;
  double ldfP5_1;
  double ldfP5_2;
  int m_23;
  int n_17;
  int d_11;
  ldfP4_0 = 0.0;
  for (d_10=1; d_10<=D; d_10++) {
    ldfP4_1 = 0.0;
    for (n_16=1; n_16<=N[d_10-1]; n_16++) {
      ldfP4_2 = 0.0;
      for (m_22=1; m_22<=M[d_10-1][n_16-1]; m_22++) {
        if(entity_map[d_10-1] == -1) {
          ldfP4_2 += ldf_Mult(1, z[d_10-1][n_16-1][m_22-1], theta[d_10-1], 1, K);
        } else {
          ldfP4_2 += ldf_Mult(1, z[d_10-1][n_16-1][m_22-1], theta_train[entity_map[d_10-1]], 1, K);
        }
      }
      ldfP4_1 += ldfP4_2;
    }
    ldfP4_0 += ldfP4_1;
    //    fprintf(stderr, "\nem=%d\tldfP4_0=%f\tldfP4_1=%f\n", entity_map[d_10-1], ldfP4_0, ldfP4_1);
  }
  ldfP5_0 = 0.0;
  for (d_11=1; d_11<=D; d_11++) {
    ldfP5_1 = 0.0;
    for (n_17=1; n_17<=N[d_11-1]; n_17++) {
      ldfP5_2 = 0.0;
      for (m_23=1; m_23<=M[d_11-1][n_17-1]; m_23++) {
        ldfP5_2 += ldf_Mult(1, w[d_11-1][n_17-1][m_23-1], beta[z[d_11-1][n_17-1][m_23-1]-1], 1, V);
      }
      ldfP5_1 += ldfP5_2;
    }
    ldfP5_0 += ldfP5_1;
  }

  return ((ldf_Gam(1, alpha, 0.1, 1)) + ((ldf_Gam(1, eta, 0.1, 1)) + ((0.0) + ((0.0) + ((ldfP4_0) + (ldfP5_0))))));
}

/* 
 * Innitializes counts based on samples from training 
 */
void zero_counts(double **counts, int D, int K, int *N, int **M, int V)
{
  int k;
  int v;

  for(k=0; k<K; k++) {
    counts[k][V] = 0;
    for(v=0; v<V; v++) {
      counts[k][v] = 0.0;
    }
  }
}

void increment_counts(double **counts, int D, int K, int *N, int **M, int V, int ***w, int ***z)
{
  int d;
  int m;
  int n;

  //fprintf(stderr, "initalize_post_from_training\n");

  //Pass through data accumulating counts
  for(d=0; d<D; d++) {
    for(n=0; n<N[d]; n++) {
      for(m=0; m<M[d][n]; m++) {
        counts[z[d][n][m]-1][V] += 1;
        counts[z[d][n][m]-1][w[d][n][m]-1] += 1.0;
      }
    }
  }
}

void decrement_counts(double **counts, int D, int K, int *N, int **M, int V, int ***w, int ***z)
{
  int d;
  int m;
  int n;

  //fprintf(stderr, "initalize_post_from_training\n");

  //Pass through data accumulating counts
  for(d=0; d<D; d++) {
    for(n=0; n<N[d]; n++) {
      for(m=0; m<M[d][n]; m++) {
        counts[z[d][n][m]-1][V] -= 1;
        counts[z[d][n][m]-1][w[d][n][m]-1] -= 1.0;
      }
    }
  }
}

/****************************** MAIN ******************************/

/*
 * Reads from stdin in an infinite loop.  Extracts entity mapping + words + labels, from stdin, and writes out topic distributions
 * input format: 
 * entity mapping, words, labels
 */
void processEntities(int K, int V, double alpha, double eta, double** post_beta, double** post_theta_train, double* global_topic_counts, int nIter) {
  double loglik,bestloglik;
  int D;
  int** M;
  int* N;
  double** post_theta;
  int*** w;
  int*** z;
  int** labels;
  int entity_map[1];
  int*** best_z;
  int V_tmp;
  int iter;

  int malloc_dim_1;
  int malloc_dim_2;
  int malloc_dim_3;

  char *line = (char *)malloc(MAXLINE * sizeof(char));
  char *word_string;
  char *label_string;
  int len=0;
  size_t nbytes=MAXLINE;

  //  w = load_discrete3(ARGV[3], &D, &N, &M, &V_tmp);
  //  labels = load_labels(ARGV[4], &D, &K);
  //entity_map = load_entity_map(ARGV[5], D);

  /* For each entity (read from stdin as tab-seperated lines) */
  while((len = getline(&line, &nbytes, stdin)) != EOF) {
    line = strtok(line, "\n");
    entity_map[0]   = atoi(strtok(line, "\t"));
    word_string  = strtok(NULL, "\t");
    label_string = strtok(NULL, "\t");

    /* Only one entity */
    D    = 1;
    N    = (int *)malloc(1 * sizeof(int));
    N[0] = 1;
    M    = (int **)malloc(1 * sizeof(int*));
    M[0] = (int *)malloc(1 * sizeof(int));
    w    = (int ***)malloc(1 * sizeof(int**));
    w[0] = (int **)malloc(1 * sizeof(int*));

    //w      = load_discrete3s(word_string, &D, &N, &M, &V_tmp);
    w[0][0] = string2array(word_string, &M[0][0]);
    labels = load_labels_s(label_string, &D, &K);

    post_theta = (double**) malloc(sizeof(double*) * (1+(D)-(1)));
    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      post_theta[malloc_dim_1-1] = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));
    }

    z = (int***) malloc(sizeof(int**) * (1+(D)-(1)));
    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      z[malloc_dim_1-1] = (int**) malloc(sizeof(int*) * (1+(N[malloc_dim_1-1])-(1)));
      for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
        z[malloc_dim_1-1][malloc_dim_2-1] = (int*) malloc(sizeof(int) * (1+((M[malloc_dim_1-1][malloc_dim_2-1]) + (1))-(1)));
      }
    }

    best_z = (int***) malloc(sizeof(int**) * (1+(D)-(1)));
    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      best_z[malloc_dim_1-1] = (int**) malloc(sizeof(int*) * (1+(N[malloc_dim_1-1])-(1)));
      for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
        best_z[malloc_dim_1-1][malloc_dim_2-1] = (int*) malloc(sizeof(int) * (1+((M[malloc_dim_1-1][malloc_dim_2-1]) + (1))-(1)));
      }
    }

    initialize_z(z, D, M, N, K);
    initialize_post_theta(post_theta, post_theta_train, entity_map, global_topic_counts, D, K, M, N, z);
    increment_counts(post_beta, D, K, N, M, V, w, z);
    
    for (iter=1; iter<=nIter; iter++) {
      //fprintf(stderr, "iter %d", iter);
      //fflush(stderr);
      resample_z(D, M, N, alpha, eta, post_beta, post_theta, post_theta_train, entity_map, w, z, labels, K, V);

      loglik = compute_log_posterior(D, K, M, N, V, alpha, post_beta, eta, post_theta, post_theta_train, entity_map, w, z);
      //fprintf(stderr, "\t%g", loglik);
      if ((iter==1)||(loglik>bestloglik)) {
        bestloglik = loglik;
        //fprintf(stderr, " *");
        best_z = (int***) realloc(best_z, sizeof(int**) * ((D) - (1) + 1));
        for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
          best_z[malloc_dim_1-1] = (int**) realloc(best_z[malloc_dim_1-1], sizeof(int*) * ((N[malloc_dim_1-1]) - (1) + 1));
          for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
            best_z[malloc_dim_1-1][malloc_dim_2-1] = (int*) realloc(best_z[malloc_dim_1-1][malloc_dim_2-1], sizeof(int) * ((M[malloc_dim_1-1][malloc_dim_2-1]) - (1) + 1));
            for (malloc_dim_3=1; malloc_dim_3<=M[malloc_dim_1-1][malloc_dim_2-1]; malloc_dim_3++) {
              best_z[malloc_dim_1-1][malloc_dim_2-1][malloc_dim_3-1] = z[malloc_dim_1-1][malloc_dim_2-1][malloc_dim_3-1];
            }
          }
        }
      }

      if(iter == nIter) {
        dump_z(D, M, N, z);
      }

      //fprintf(stderr, "\n");
      //fflush(stderr);
    }

    decrement_counts(post_beta, D, K, N, M, V, w, z);

    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
        free(best_z[malloc_dim_1-1][malloc_dim_2-1]);
      }
      free(best_z[malloc_dim_1-1]);
    }
    free(best_z);

    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
        free(z[malloc_dim_1-1][malloc_dim_2-1]);
      }
      free(z[malloc_dim_1-1]);
    }
    free(z);

    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      for (malloc_dim_2=1; malloc_dim_2<=N[malloc_dim_1-1]; malloc_dim_2++) {
        free(w[malloc_dim_1-1][malloc_dim_2-1]);
      }
      free(w[malloc_dim_1-1]);
    }
    free(w);

    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      free(post_theta[malloc_dim_1-1]);
    }
    free(post_theta);

    free(N);

    for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
      free(M[malloc_dim_1-1]);
    }
    free(M);
  }

  return;
}

int main(int ARGC, char *ARGV[]) {
  int D_train;
  int K;
  int** M_train;
  int* N_train;
  int V;
  int V_tmp;
  int tmp;
  double alpha;
  double eta;
  double** post_beta;
  double** post_theta_train;
  double* global_topic_counts;
  int*** w_train;
  int*** z_train;
  int* entity_map;
  int malloc_dim_1;
  int malloc_dim_2;
  int malloc_dim_3;
  int nIter;
  int dumpInterval;

  if(ARGC != 5) {
    fprintf(stderr, "usage %s <train_w> <train_z> <nIter> <dumpInterval>\n", ARGV[0]);
    exit(1);
  }

  //fprintf(stderr, "-- This program was automatically generated using HBC (v 0.7 beta) from LDA.hier\n--     see http://hal3.name/HBC for more information\n");
  //fflush(stderr);
  setall(time(0),time(0));   /* initialize random number generator */


  /* variables defined with --define */
  K = 19;
  alpha = 0.1;
  //alpha = 1.0;
  eta = 0.1;

  //fprintf(stderr, "Loading data...\n");
  //fflush(stderr);

  /* "Training" data */
  w_train = load_discrete3(ARGV[1], &D_train, &N_train, &M_train, &V);
  z_train = load_discrete3(ARGV[2], &D_train, &N_train, &M_train, &tmp);

  /* variables defined with --loadD */
  nIter = atoi(ARGV[3]);

  /* variables defined with --loadM or --loadMI */
  //fprintf(stderr, "Allocating memory...\n");
  //fflush(stderr);
  post_beta = (double**) malloc(sizeof(double*) * (1+(K)-(1)));
  for (malloc_dim_1=1; malloc_dim_1<=K; malloc_dim_1++) {
    post_beta[malloc_dim_1-1] = (double*) malloc(sizeof(double) * (1+((V) + (1))-(1)));
  }

  global_topic_counts = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));

  post_theta_train = (double**) malloc(sizeof(double*) * (1+(D_train)-(1)));
  for (malloc_dim_1=1; malloc_dim_1<=D_train; malloc_dim_1++) {
    post_theta_train[malloc_dim_1-1] = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));
  }

  //fprintf(stderr, "Initializing variables...\n");
  //fflush(stderr);

  initialize_global_topic_counts(z_train, global_topic_counts, D_train, K, M_train, N_train);

  initialize_post_theta(post_theta_train, NULL, NULL, NULL, D_train, K, M_train, N_train, z_train);

  /* initialize_post_beta(post_beta, D, K, M, N, V, w, z); */
  zero_counts(post_beta, D_train, K, N_train, M_train, V);
  increment_counts(post_beta, D_train, K, N_train, M_train, V, w_train, z_train);

  /*****************************************************
    NOTE: we could free w_train and z_train
    at this point, but it doesn't seem to be necessary
  ******************************************************/

  processEntities(K, V, alpha, eta, post_beta, post_theta_train, global_topic_counts, nIter);

  //printf("ll = %g\n", bestloglik);
  //dump_z(D, M, N, best_z);
  //dump_z(D, M, N, z);

  for (malloc_dim_1=1; malloc_dim_1<=K; malloc_dim_1++) {
    free(post_beta[malloc_dim_1-1]);
  }
  free(post_beta);

  return 0;
}
