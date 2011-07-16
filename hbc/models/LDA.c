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

  gcc -O3 -lm stats.c samplib.c LDA.c -o LDA.out

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
*/
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "stats.h"


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

void resample_post_theta(int D, int K, int** M, int* N, double** post_theta, int*** z) {
  int d_9;
  double* tmpSP7;
  int n_3;
  int m_75;
  int dvv_loop_var_1;
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
    sample_Delta(post_theta[d_9-1], tmpSP7, K);
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

void resample_z(int D, int** M, int* N, double alpha, double eta, double** post_beta, double** post_theta, int*** w, int*** z, int K, int V) {
  int d_10;
  int n_16;
  int m_22;
  double* tmp_post_z_3;
  int tmp_idx_z_3;
  int dvv_loop_var_1;
  tmp_post_z_3 = (double*) malloc(sizeof(double) * (1+((K) + (1))-(1)));
  for (d_10=1; d_10<=D; d_10++) {
    for (n_16=1; n_16<=N[d_10-1]; n_16++) {
      for (m_22=1; m_22<=M[d_10-1][n_16-1]; m_22++) {
        post_theta[d_10-1][(K) + (1)-1] += (0.0) - (1.0);
        post_theta[d_10-1][z[d_10-1][n_16-1][m_22-1]-1] += (0.0) - (1.0);
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][(V) + (1)-1] += (0.0) - ((1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0)));
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][w[d_10-1][n_16-1][m_22-1]-1] += (0.0) - ((1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0)));
        /* Implements multinomial sampling from the following distribution: */
        /*   (Mult(w_{d@10,n@16,m@22} | .+(eta, sub(post_beta, z_{d@10,n@16,m@22}))))(Mult(z_{d@10,n@16,m@22} | .+(alpha, post_theta_{d@10}))) */
        for (dvv_loop_var_1=1; dvv_loop_var_1<=K; dvv_loop_var_1++) {
          tmp_post_z_3[dvv_loop_var_1-1] = 0.0;
        }
        tmp_post_z_3[(K) + (1)-1] = (0.0) * (((1) + (K)) - (1));
        for (tmp_idx_z_3=1; tmp_idx_z_3<=K; tmp_idx_z_3++) {
          tmp_post_z_3[tmp_idx_z_3-1] = (ldf_Mult_smooth(0, eta, w[d_10-1][n_16-1][m_22-1], post_beta[tmp_idx_z_3-1], 1, V)) + (ldf_Mult_smooth(0, alpha, tmp_idx_z_3, post_theta[d_10-1], 1, K));
        }
        normalizeLog(tmp_post_z_3, 1, K);
        z[d_10-1][n_16-1][m_22-1] = sample_Mult(tmp_post_z_3, 1, K);
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][(V) + (1)-1] += (1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0));
        post_beta[z[d_10-1][n_16-1][m_22-1]-1][w[d_10-1][n_16-1][m_22-1]-1] += (1.0) * ((((z[d_10-1][n_16-1][m_22-1]) == (z[d_10-1][n_16-1][m_22-1])) ? 1 : 0));
        post_theta[d_10-1][(K) + (1)-1] += 1.0;
        post_theta[d_10-1][z[d_10-1][n_16-1][m_22-1]-1] += 1.0;
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

void initialize_post_theta(double** post_theta, int D, int K, int** M, int* N, int*** z) {
  int dvv_loop_var_1;
  int dvv_loop_var_2;
  for (dvv_loop_var_1=1; dvv_loop_var_1<=D; dvv_loop_var_1++) {
    for (dvv_loop_var_2=1; dvv_loop_var_2<=K; dvv_loop_var_2++) {
      post_theta[dvv_loop_var_1-1][dvv_loop_var_2-1] = 0.0;
    }
    post_theta[dvv_loop_var_1-1][(K) + (1)-1] = (0.0) * (((1) + (K)) - (1));
  }
  resample_post_theta(D, K, M, N, post_theta, z);
}


/**************************** DUMPING *****************************/

void dump_alpha(double alpha) {
  printf("alpha = ");
  printf("%g", alpha);
  printf("\n");
}

void dump_eta(double eta) {
  printf("eta = ");
  printf("%g", eta);
  printf("\n");
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
  printf("\n");
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
  printf("\n");
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
  printf("\n");
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
  printf("\n");
}


/*************************** LIKELIHOOD ***************************/

double compute_log_posterior(int D, int K, int** M, int* N, int V, double alpha, double** beta, double eta, double** theta, int*** w, int*** z) {
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
        ldfP4_2 += ldf_Mult(1, z[d_10-1][n_16-1][m_22-1], theta[d_10-1], 1, K);
      }
      ldfP4_1 += ldfP4_2;
    }
    ldfP4_0 += ldfP4_1;
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

/****************************** MAIN ******************************/

int main(int ARGC, char *ARGV[]) {
  double loglik,bestloglik;
  int iter;
  int D;
  int K;
  int** M;
  int* N;
  int V;
  double alpha;
  double eta;
  double** post_beta;
  double** post_theta;
  int*** w;
  int*** z;
  int*** best_z;
  int malloc_dim_1;
  int malloc_dim_2;
  int malloc_dim_3;

  fprintf(stderr, "-- This program was automatically generated using HBC (v 0.7 beta) from LDA.hier\n--     see http://hal3.name/HBC for more information\n");
  fflush(stderr);
  setall(time(0),time(0));   /* initialize random number generator */


  /* variables defined with --define */
  K = 40;
  alpha = 0.1;
  eta = 0.1;

  fprintf(stderr, "Loading data...\n");
  fflush(stderr);
  /* variables defined with --loadD */
  w = load_discrete3("test", &D, &N, &M, &V);

  /* variables defined with --loadM or --loadMI */

  fprintf(stderr, "Allocating memory...\n");
  fflush(stderr);
  post_beta = (double**) malloc(sizeof(double*) * (1+(K)-(1)));
  for (malloc_dim_1=1; malloc_dim_1<=K; malloc_dim_1++) {
    post_beta[malloc_dim_1-1] = (double*) malloc(sizeof(double) * (1+((V) + (1))-(1)));
  }

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


  fprintf(stderr, "Initializing variables...\n");
  fflush(stderr);
  initialize_z(z, D, M, N, K);
  initialize_post_beta(post_beta, D, K, M, N, V, w, z);
  initialize_post_theta(post_theta, D, K, M, N, z);

  for (iter=1; iter<=100; iter++) {
    fprintf(stderr, "iter %d", iter);
    fflush(stderr);
    resample_z(D, M, N, alpha, eta, post_beta, post_theta, w, z, K, V);

    loglik = compute_log_posterior(D, K, M, N, V, alpha, post_beta, eta, post_theta, w, z);
    fprintf(stderr, "\t%g", loglik);
    if ((iter==1)||(loglik>bestloglik)) {
      bestloglik = loglik;
      fprintf(stderr, " *");
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
    fprintf(stderr, "\n");
    fflush(stderr);
  }

  printf("ll = %g\n", bestloglik);
  dump_z(D, M, N, best_z);

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

  for (malloc_dim_1=1; malloc_dim_1<=K; malloc_dim_1++) {
    free(post_beta[malloc_dim_1-1]);
  }
  free(post_beta);

  free(N);

  for (malloc_dim_1=1; malloc_dim_1<=D; malloc_dim_1++) {
    free(M[malloc_dim_1-1]);
  }
  free(M);


  return 0;
}
