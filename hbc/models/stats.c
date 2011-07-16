#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "stats.h"
#include "samplib.h"

/* extraneous functions */

double NEGINF = -0/1;
double epsilonValue = 1e-10;

#define BOUNDLO(x) (((x)<epsilonValue)?(epsilonValue):(x))
#define BOUNDHI(x) (((x)>(1-epsilonValue))?(1-epsilonValue):(x))
#define BOUND(x) (BOUNDLO(BOUNDHI(x)))
#define BOUNDPROB(x) (((x)<-300)?(-300):((((x)>300)?(300):(x))))

inline double factln(double x) { return gammaln(x+1); }

inline double addLog(double x, double y) {
  if (x==NEGINF) { return y; }
  if (y==NEGINF) { return x; }

  if (x-y > 16) { return x; }
  else if (x > y) { return x + log(1 + exp(y-x)); }
  else if (y-x > 16) { return y; }
  else { return y + log(1 + exp(x-y)); }
}

void normalizeLog(double*x, int lo, int hi) {
  double s;
  int i;
  s = NEGINF;
  for (i=0; i<=hi-lo; i++) s = addLog(s, x[i]);
  for (i=0; i<=hi-lo; i++) x[i] = exp(x[i] - s);

  x[hi-lo+1] = 1;  // store sum
    /*  for (i=lo-1;i<hi;i++) { s = addLog(s, x[i]); }
        for (i=lo-1;i<hi;i++) { x[i] = exp(x[i] - s); } */
}


/* sampling functions */

inline int sample_Poi(double mu) {
  return (int)ignpoi(mu);
}

inline int sample_MultSym(int lo, int hi) {
  return lo + (int)(ranf() * (double)(hi-lo+1));
}

int sample_Mult(double*th, int lo, int hi) {
  double s;
  int i;
  // TODO: we shouldn't have to compute the sum
  s = th[hi-lo+1];
  //for (i=0; i<=hi-lo; i++) { s += th[i]; }
  s = ranf() * s;
  for (i=0; i<=hi-lo; i++) {
    s -= th[i];
    if (s<0) { return i+lo; }
  }
  return lo;
}

int sample_Mult_smooth(double eta, double*th, int lo, int hi) {
  double s;
  int i;
  // TODO: we shouldn't have to compute the sum
  //s = 0;
  //for (i=0; i<=hi-lo; i++) { s += th[i] + eta; }
  s = th[hi-lo+1] + eta*(hi-lo+1);
  s = ranf() * s;
  for (i=0; i<=hi-lo; i++) {
    s -= th[i] + eta;
    if (s<0) { return i+lo; }
  }
  return lo;
}

void sample_DirSym(double*th, double al, int dim) {
  int i;
  double s;
  s = 0;
  for (i=0; i<dim; i++) {
    th[i] = BOUNDLO(gengam(1.0,al));
    s += th[i];
  }
  for (i=0; i<dim; i++) { th[i] = BOUND(th[i]/s); }
  th[dim] = 1;  // store the sum
}

void sample_Dir(double*th, double*al, int dim) {
  int i;
  double s;
  s = 0;
  for (i=0; i<dim; i++) {
    th[i] = BOUNDLO(gengam(1.0,al[i]));
    s += th[i];
  }
  for (i=0; i<dim; i++) { th[i] = BOUND(th[i]/s); }
  th[dim] = 1;  // store the sum
}

double sample_Gam(double a, double b) {
  return BOUNDLO(gengam(1/b,a));
}

double sample_Bet(double a, double b) {
  return BOUND(genbet(a,b));
}

int sample_Bin(double pi) {
  return (ranf() < pi);
}

double sample_Nor(double mu, double si2) {
  return si2*snorm()+mu;
}

void sample_NorMV(double*x, double*mu, double si2, int lo, int hi) {
  int i;
  double s = 0;
  for (i=0; i<=hi-lo; i++) {
    x[i] = si2*snorm()+mu[i];
    s = s + x[i];
  }
  x[hi-lo+1] = s;
}

double sample_Exp(double la) {
  return BOUNDLO(genexp(la));
}

void sample_Delta(double*dst, double*src, int hi) {
  int i;
  for (i=0; i<=hi; i++) { // <= because we copy the sum
    dst[i] = src[i];
  }
}

double sample_Unif(double lo, double hi) {
  return lo + ranf() * (hi - lo);
}

// if we currently have K clusters, then pi is a distribution over K+1
// items, which means that it's a vector of length K+2 (the last
// position is used to store the sum of pi).  counts will be a vector
// over K+1 items, which means it will also have K+2 elements.
void   sample_PY(double*pi, double alpha, double delta, int K, double*counts, int*Knew, double**pinew) {
  // this is just like a dirichlet sample, but with (a) discounting
  // and (b) variable number of clusters we end up sampling from
  // Dir(Z, K+1), where Z(k) = (alpha+delta*K)/Kunused if k is unused
  // and = counts(k) - delta, if k is used.  Kunused in the number of
  // unused clusters finally, if everything is used, we need to add a
  // single unused slot
  int Kunused;
  int k;
  double s;
  double*oldpi;

  // how many unused slots are there?
  Kunused = 0;
  for (k=0; k<K+1; k++) {
    if (counts[k] <= 0) { Kunused++; }
  }

  if (Kunused > 0) {  // there are unused slots: this is the easy case
    // store the posterior in "pi"
    s = 0;
    for (k=0; k<K+1; k++) {
      if (counts[k] > 0) {
        pi[k] = counts[k] - delta;
      } else {
        pi[k] = (alpha + delta * (double)(K-Kunused)) / (double)Kunused;
      }
      s += pi[k];
    }
    pi[K+1] = s;  // store sum

    // set return values
    *Knew = K;
    *pinew = pi;
  } else {
    // if there are no unused slots, make one!
    oldpi = pi;
    pi = (double*) realloc(pi, (K+3)*sizeof(double));
    //fprintf(stderr, "reallocating pi to %d\t(%p to %p)\n", K+3, oldpi, pi);
    if (!pi) { fprintf(stderr, "accckkk!"); }
    pi[K+2] = 0;

    // store posterior in pi
    s = 0;
    for (k=0; k<K+1; k++) {
      pi[k] = counts[k] - delta;
      s += pi[k];
    }
    pi[K+1] = (alpha + delta * (double)K);
    pi[K+2] = s + pi[K+1];  // store sum

    // set return values
    *Knew = K+1;
    *pinew = pi;
  }
}


/* mode functions */

int mode_Poi(double mu) {
  return (int)(mu + 1e-10);
}

int mode_MultSym(int lo, int hi) {
  return lo + (int)(ranf() * (double)(hi-lo+1));
}

int mode_Mult(double*th, int lo, int hi) {
  int i,j;
  i = 0;
  for (j=1; j<=hi-lo; j++) {
    if (th[j] > th[i]) { i = j; }
  }
  return i+lo;
}

void mode_DirSym(double*th, double al, int dim) {
  int i;
  for (i=0; i<dim; i++) {
    th[i] = 1.0 / (double)dim;
  }
  th[dim] = 1; // store the sum
}

void mode_Dir(double*th, double*al, int dim) {
  int i;
  double s;
  s = 0;
  for (i=0; i<dim; i++) {
    s = s + al[i];
  }
  for (i=0; i<dim; i++) { th[i] = BOUND(al[i]/s); }
  th[dim] = 1;
}

double mode_Gam(double a, double b) {
  return BOUNDLO((a-1)*b);
}

double mode_Bet(double a, double b) {
  if ((a>1) && (b>1)) {
    return ((a-1)/(a+b-2));
  } else {
    // return  mean
    return (a/(a+b));
  }
}

int mode_Bin(double pi) {
  return (pi > 0.5);
}

double mode_Nor(double mu, double si2) {
  return mu;
}

void mode_NorMV(double*x, double*mu, double si2, int lo, int hi) {
  int i;
  for (i=0; i<=hi-lo+1; i++) { // +1 because store the sum
    x[i] = mu[i];
  }
}

double mode_Exp(double la) {
  return 0;
}

void mode_Delta(double*dst, double*src, int hi) {
  int i;
  for (i=0; i<=hi; i++) {  // <= to copy the sum
    dst[i] = src[i];
  }
}


/* likelihood functions */

double ldf_Poi(int normalize, int x, double la) {
  return BOUNDPROB(-factln((double)x) - ((double)x)*log(la) - la);  // normalize no matter what
}

double ldf_MultSym(int normalize, int x, int lo, int hi) {
  if ((x<lo)||(x>hi)) { return NEGINF; }
  return BOUNDPROB(-log((double)(hi-lo+1)));
}

double ldf_Mult(int normalize, int x, double*th, int lo, int hi) {
  double s;
  int i;
  // TODO: we shouldn't have to compute the sum
  if ((x<lo)||(x>hi)) { return NEGINF; }
  //s = 0;
  //for (i=0; i<=hi-lo; i++) { s+=th[i]; }
  s = th[hi-lo+1];
  return BOUNDPROB(log(th[x-lo]) - log(s));
}

double ldf_Mult_smooth(int normalize, double eta, int x, double*th, int lo, int hi) {
  double s;
  int i;
  // TODO: we shouldn't have to compute the sum
  if ((x<lo)||(x>hi)) { return NEGINF; }
  //s = eta*(hi-lo+1);
  //for (i=hi-lo; i>=0; i--) { s+=th[i]; }
  s = th[hi-lo+1] + eta*(hi-lo+1);
  return BOUNDPROB(log(th[x-lo]+eta) - log(s));
}

double ldf_DirSym(int normalize, double*th, double al, int dim) {
  double l;
  double a;
  double s;
  int i;
  // TODO: we shouldn't have to compute the sum
  a = al*((double)dim);
  s = th[dim];
  l = 0;
  if (normalize) {
    l = gammaln(a) - ((double)dim) * gammaln(al);
  }
  //for (i=0;i<dim;i++) { s += th[i]; }
  for (i=0;i<dim;i++) { l += (al-1) * log(BOUND(th[i]/s)); }
  return BOUNDPROB(l);
}

double ldf_Dir(int normalize, double*th, double*al, int dim) {
  double l;
  double a;
  double s;
  // TODO: we shouldn't have to compute the sum
  int i;
  a = al[dim];
  s = th[dim];
  l = 0;
  //for (i=0;i<dim;i++) { s += th[i]; a += al[i]; if (normalize ) { l -= gammaln(al[i]); } }
  if (normalize) {
    for (i=0;i<dim;i++) 
      l -= gammaln(al[i]);
    l += gammaln(a);
  }
  for (i=0;i<dim;i++) { l += (al[i]-1) * log(th[i]/s); }
  return BOUNDPROB(l);
}

double ldf_Gam(int normalize, double x, double a, double b) {
  if (x < 0) { return NEGINF; }
  return BOUNDPROB((normalize ? (-a*log(b) - gammaln(a)) : (0.0)) + (a-1)*log(x) - x/b);
}

double ldf_Bet(int normalize, double x, double a, double b) {
  if ((x < 0) || (x > 1)) { return NEGINF; }
  return BOUNDPROB((normalize ? (gammaln(a+b)-gammaln(a)-gammaln(b)) : (0.0)) + (a-1)*log(x) + (b-1)*log(1-x));
}

double ldf_Bin(int normalize, int x, double pi) {
  if (x) { return BOUNDPROB(log(pi)); } else { return BOUNDPROB(log(1-pi)); }
}

double ldf_Nor(int normalize, double x, double mu, double si2) {
  return BOUNDPROB((normalize ? (-0.5*log(2*3.1416*si2)) : (0.0)) - 0.5*(x-mu)*(x-mu)/si2);
}

double ldf_NorMV(int normalize, double*x, double*mu, double si2, int lo, int hi) {
  double s;
  int i;
  s = 0;
  for (i=0;i<=hi-lo;i++) {
    s += (x[i]-mu[i]) * (x[i]-mu[i]);
  }
  return BOUNDPROB((normalize ? (-((double)(hi-lo+1))/2 * log(2*3.1416*si2)) : (0.0)) - 0.5 * s / si2);
}

double ldf_Exp(int normalize, double x, double la) {
  if (x < 0) { return NEGINF; }
  return BOUNDPROB(log(la) - la * x);  // normalize no matter what
}

double ldf_PY(int normalize, double*pi, double alpha, double delta, int K) {  // WARNING: this is approximate!
  double l;
  double a;
  double s;
  int i;

  a = 0;
  s = 0;
  l = 0;
  for (i=0; i<=K; i++) if (pi[i] - alpha >= 1) { a += alpha; s += pi[i]-alpha; }

  if (normalize) { 
    l = gammaln(a) - ((double)(K+1)) * gammaln(alpha); 
  }
  for (i=0; i<=K; i++) {
    if (pi[i] - alpha >= 1) {
      l += (alpha-1) * log(BOUND((pi[i]-alpha)/s));
    }
  }

  return BOUNDPROB(l);
}

/* utility functions */

double** load_matrix(char*fname, int*N, int*dim) {
  FILE *f;
  double**x;
  int i,j,k;
  double tmp;
  double sum;
  *N = 0; *dim = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%*[^\n]%*[\n]");
    k++;
  }
  fclose(f);
  *N = k;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%lg", &tmp);
    k++;
  }
  fclose(f);

  *dim = (k / *N);

  f = fopen(fname, "r");
  x = malloc(*N * sizeof(double*));
  for (i=0; i<*N; i++) {
    x[i] = malloc((*dim+1) * sizeof(double));
    sum = 0;
    for (j=0; j<*dim; j++) {
      k = fscanf(f, "%lg", &tmp);
      x[i][j] = tmp;
      sum = sum + tmp;
    }
    x[i][*dim] = sum;
  }
  fclose(f);

  return x;
}

int** load_matrix_int(char*fname, int*N, int*dim) {
  FILE *f;
  int**x;
  int i,j,k;
  int tmp;

  *N = 0; *dim = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%*[^\n]%*[\n]");
    k++;
  }
  fclose(f);
  *N = k;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%d", &tmp);
    k++;
  }
  fclose(f);

  *dim = (k / *N);

  f = fopen(fname, "r");
  x = malloc(*N * sizeof(double*));
  for (i=0; i<*N; i++) {
    x[i] = malloc(*dim * sizeof(double));
    for (j=0; j<*dim; j++) {
      k = fscanf(f, "%d", &tmp);
      x[i][j] = tmp;
    }
  }
  fclose(f);

  return x;
}

int* load_discrete1(char*fname, int*dim, int*max) {
  FILE *f;
  int*x;
  int i,j,k;

  *dim = 0;
  *max = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%d", &j);
    if (i > 0) { 
      k++; 
      if (j > *max) { *max = j; }
    }
  }
  *dim = k;
  fclose(f);

  x = malloc(*dim * sizeof(int));

  f = fopen(fname, "r");
  j = 0;
  while (!feof(f)) {
    i = fscanf(f, "%d", &k);
    if (i > 0) {
      x[j] = k;
      j++;
    }
  }
  fclose(f);

  return x;
}

int** load_discrete2(char*fname, int*dim1, int**dim2, int*max) {
  FILE *f;
  int**x;
  int*tmp;
  char*s;
  int i,j,k,l,maxlen;

  *max = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    i = fscanf(f, "%*[^\n]%*[\n]");
    k++;
  }
  fclose(f);
  *dim1 = k;

  x     = malloc(*dim1 * sizeof(int*));
  *dim2 = malloc(*dim1 * sizeof(int));

  s   = malloc(1000000 * sizeof(char));
  tmp = malloc(1000000 * sizeof(int));

  f = fopen(fname, "r");
  k = 0;
  while (!feof(f)) {
    l = 0;
    i = 1;
    while (1) {
      i = fscanf(f, "%[^ \n]", s);
      if (i <= 0) { break; }
      tmp[l] = atoi(s);
      if (tmp[l] > *max) { *max = tmp[l]; }
      l++;
      i = fscanf(f, "%[ \n]", s);
      if (s[0] == '\n') { break; }
    }
    x[k] = malloc(l * sizeof(int));
    for (j=0; j<l; j++) {
      x[k][j] = tmp[j];
    }
    (*dim2)[k] = l;
    k++;
    for (i=1; i<strlen(s); i++) {
      x[k] = NULL;
      (*dim2)[k] = 0;
      k++;
    }
  }
  fclose(f);

  free(s);
  free(tmp);

  return x;
}

int*** load_discrete3(char*fname, int*dim1, int**dim2, int***dim3, int*max) {
  FILE *f;
  int***x;
  char*s;
  int i,j,k,l,maxlen,v;
  char c;
  int*tmp;

  *max = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { k++; }
  }
  fclose(f);
  *dim1 = k;

  *dim2 = malloc(*dim1 * sizeof(int));
  k = 0;
  i = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { 
      (*dim2)[k] = i;
      k++;
      i = 0;
    } else {
      if (i == 0) { i = 1; }
      if (c == '\t') { 
        i++;
      }
    }
  }
  fclose(f);

  *dim3 = malloc(*dim1 * sizeof(int*));
  for (k=0; k<*dim1; k++) {
    (*dim3)[k] = malloc((*dim2)[k] * sizeof(int));
  }
  k = 0;
  i = 0;
  j = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { 
      (*dim3)[k][i] = j;
      //fprintf(stderr,"A: dim3[%d][%d] = %d\n", k, i, (*dim3)[k][i]);
      k++;
      i = 0;
      j = 0;
    } else if (c == '\t') { 
      (*dim3)[k][i] = j;
      //fprintf(stderr,"B: dim3[%d][%d] = %d\n", k, i, (*dim3)[k][i]);
      i++;
      j = 0;
    } else if (c == ' ') { 
      j++; 
    } else if (j == 0) { j = 1; }
  }
  fclose(f);

  x = malloc(*dim1 * sizeof(int**));
  //fprintf(stderr,"dim1 = %d\n", *dim1);
  for (k=0; k<*dim1; k++) {
    //fprintf(stderr,"dim2[%d] = %d\n", k, (*dim2)[k]);
    x[k] = malloc((*dim2)[k] * sizeof(int*));
    for (i=0; i<(*dim2)[k]; i++) {
      //fprintf(stderr,"dim3[%d][%d] = %d\n", k, i, (*dim3)[k][i]);
      x[k][i] = malloc((*dim3)[k][i] * sizeof(int));
    }
  }

  f = fopen(fname, "r");
  k = 0;
  i = 0;
  j = 0;
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c <= 0) { break; }
    //fprintf(stderr,"[%d:%c]",c,c);
    if (c == ' ') {
    } else if (c == '\n') {
      k++;
      i=0;
      j=0;
    } else if (c == '\t') {
      i++;
      j=0;
    } else {
      ungetc(c, f);
      l = fscanf(f, "%d", &v);
      x[k][i][j] = v;
      if (v > *max) { *max = v; }
      //fprintf(stderr,"x[%d][%d][%d] = %d\n", k, i, j, v);
      j++;
    }
  }
  fclose(f);

  /*
  fprintf(stderr,"\n\nx=\n");
  for (k=0; k<*dim1; k++) {
    for (i=0; i<(*dim2)[k]; i++) {
      for (j=0; j<(*dim3)[k][i]; j++) {
        fprintf(stderr,"%d ", x[k][i][j]);
      }
      fprintf(stderr,"\t");
    }
    fprintf(stderr,"\n");
  }
  */

  return x;
}

int* string2array(char*input, int*dim)
{
  int *result;
  char *s;
  char buffer[1024];
  int n;
  
  /* First pass, figure out how much memory to allocate */
  strcpy(buffer, input);
  s = strtok(buffer, " ");
  n = 0;
  do {
    n++;
  } while((s = strtok(NULL, " ")) != NULL);

  *dim = n;
  result = (int *)malloc(n * sizeof(int));

  /* Second pass, read it in */
  strcpy(buffer, input);
  s = strtok(buffer, " ");
  n = 0;
  do {
    result[n] = atoi(s);
    n++;
  } while((s = strtok(NULL, " ")) != NULL);
  
  return result;
}

int**** load_discrete4(char*fname, int*dim1, int**dim2, int***dim3, int****dim4, int*max) {
  FILE *f;
  int****x;
  char*s;
  int i,j,k,l,m,maxlen,v;
  char c;
  int*tmp;

  *max = 0;

  k = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { k++; }
  }
  fclose(f);
  *dim1 = k;

  *dim2 = malloc(*dim1 * sizeof(int));
  k = 0;
  i = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { 
      (*dim2)[k] = i;
      k++;
      i = 0;
    } else {
      if (i == 0) { i = 1; }
      if (c == '\t') { 
        i++;
      }
    }
  }
  fclose(f);

  *dim3 = malloc(*dim1 * sizeof(int*));
  for (k=0; k<*dim1; k++) {
    (*dim3)[k] = malloc((*dim2)[k] * sizeof(int));
  }

  k = 0;
  i = 0;
  j = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { 
      (*dim3)[k][i] = j;
      k++;
      i = 0;
      j = 0;
    } else if (c == '\t') { 
      (*dim3)[k][i] = j;
      i++;
      j = 0;
    } else if (c == '#') { 
      j++; 
    } else if (j == 0) { j = 1; }
    
  }
  fclose(f);

  *dim4 = malloc(*dim1 * sizeof(int**));
  for (k=0; k<*dim1; k++) {
    (*dim4)[k] = malloc((*dim2)[k] * sizeof(int*));
    for (i=0; i<(*dim2)[k]; i++) {
      (*dim4)[k][i] = malloc((*dim3)[k][i] * sizeof(int));
    }
  }

  k = 0;
  i = 0;
  j = 0;
  l = 0;
  f = fopen(fname, "r");
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c == '\n') { 
      (*dim4)[k][i][j] = l;
      k++;
      i = 0;
      j = 0;
      l = 0;
    } else if (c == '\t') { 
      (*dim4)[k][i][j] = l;
      i++;
      j = 0;
      l = 0;
    } else if (c == '#') { 
      (*dim4)[k][i][j] = l;
      j++;
      l = 0;
    } else if (c == ' ') { 
      l++; 
    } else if (l == 0) { l = 1; }
  }
  fclose(f);

  x = malloc(*dim1 * sizeof(int***));
  //fprintf(stderr,"dim1 = %d\n", *dim1);
  for (k=0; k<*dim1; k++) {
    //fprintf(stderr,"dim2[%d] = %d\n", k, (*dim2)[k]);
    x[k] = malloc((*dim2)[k] * sizeof(int**));
    for (i=0; i<(*dim2)[k]; i++) {
      //fprintf(stderr,"dim3[%d][%d] = %d\n", k, i, (*dim3)[k][i]);
      x[k][i] = malloc((*dim3)[k][i] * sizeof(int*));
      for (j=0; j<(*dim3)[k][i]; j++) {
        //fprintf(stderr,"dim4[%d][%d][%d] = %d\n", k, i, j, (*dim4)[k][i][j]);
        x[k][i][j] = malloc((*dim4)[k][i][j] * sizeof(int));
      }
    }
  }

  f = fopen(fname, "r");
  k = 0;
  i = 0;
  j = 0;
  l = 0;
  while (!feof(f)) {
    c = (char)fgetc(f);
    if (c <= 0) { break; }
    if (c == ' ') {
    } else if (c == '\n') {
      k++;
      i=0;
      j=0;
      l=0;
    } else if (c == '\t') {
      i++;
      j=0;
      l=0;
    } else if (c == '#') {
      j++;
      l=0;
    } else {
      ungetc(c, f);
      m = fscanf(f, "%d", &v);
      //fprintf(stderr,"x[%d][%d][%d][%d] = %d\n", k, i, j, l, v);
      x[k][i][j][l] = v;
      if (v > *max) { *max = v; }
      l++;
    }
  }
  fclose(f);

  /*
  fprintf(stderr,"\n\nx=\n");
  for (k=0; k<*dim1; k++) {
    for (i=0; i<(*dim2)[k]; i++) {
      for (j=0; j<(*dim3)[k][i]; j++) {
        for (l=0; l<(*dim4)[k][i][j]; l++) {
          fprintf(stderr,"%d ", x[k][i][j][l]);
        }
        fprintf(stderr,"#");
      }
      fprintf(stderr,"\t");
    }
    fprintf(stderr,"\n");
  }
  */
  return x;
}


double*   IDR(double*res, int pos, int lo, int hi) {
  int i;
  for (i=0;i<=hi-lo+1;i++) res[i] = 0.;  // +1 to store sum
  if ((pos>=lo) && (pos<=hi)) {
    res[pos-lo]  = 1.;
    res[hi-lo+1] = 1.;
  }
  return res;
}

int   *   ID (int   *res, int pos, int lo, int hi) {
  int i;
  for (i=0;i<=hi-lo+1;i++) res[i] = 0;  // +1 to store sum
  if ((pos>=lo) && (pos<=hi)) {
    res[pos-lo]  = 1;
    res[hi-lo+1] = 1;
  }
  return res;
}


double*   add_const_r_1 (double*   res, double cn, double*   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1;i++) res[i] = cn + vec[i];
  res[hi1-lo1+1] += cn*(hi1-lo1+1);
  return res;
}

double**  add_const_r_2 (double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) res[i][j] = cn + vec[i][j];
    res[i][hi2-lo2+1] += cn*(hi2-lo2+1);
  }
  return res;
}

double*** add_const_r_3 (double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) res[i][j][k] = cn + vec[i][j][k];
      res[i][j][hi3-lo3+1] += cn*(hi3-lo3+1);
    }
  return res;
}

double*   sub_const_r_1 (double*   res, double cn, double*   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1;i++) res[i] = cn - vec[i];
  res[hi1-lo1+1] -= cn*(hi1-lo1+1);
  return res;
}

double**  sub_const_r_2 (double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) res[i][j] = cn - vec[i][j];
    res[i][hi2-lo2+1] -= cn*(hi2-lo2+1);
  }
  return res;
}

double*** sub_const_r_3 (double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) res[i][j][k] = cn - vec[i][j][k];
      res[i][j][hi3-lo3+1] -= cn*(hi3-lo3+1);
    }

  return res;
}

double*   mult_const_r_1 (double*   res, double cn, double*   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = cn * vec[i];
  return res;
}

double**  mult_const_r_2 (double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = cn * vec[i][j];
  return res;
}

double*** mult_const_r_3 (double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = cn * vec[i][j][k];
  return res;
}

double*   add_vec_r_1   (double*   res, double*   vec1, double*   vec2, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = vec1[i] + vec2[i];
  return res;
}

double**  add_vec_r_2   (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = vec1[i][j] + vec2[i][j];
  return res;
}

double*** add_vec_r_3   (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = vec1[i][j][k] + vec2[i][j][k];
  return res;
}

double*   sub_vec_r_1   (double*   res, double*   vec1, double*   vec2, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = vec1[i] - vec2[i];
  return res;
}

double**  sub_vec_r_2   (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = vec1[i][j] - vec2[i][j];
  return res;
}

double*** sub_vec_r_3   (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = vec1[i][j][k] - vec2[i][j][k];
  return res;
}

double*   mult_vec_r_1   (double*   res, double*   vec1, double*   vec2, int lo1, int hi1) {
  int i;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) { res[i] = vec1[i] * vec2[i]; sum += res[i]; }
  res[hi1-lo1+1] = sum;
  return res;
}

double**  mult_vec_r_2   (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) { res[i][j] = vec1[i][j] * vec2[i][j]; sum += res[i][j]; }
    res[i][hi2-lo2+1] = sum;
    sum = 0;
  }
  return res;
}

double*** mult_vec_r_3   (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) { res[i][j][k] = vec1[i][j][k] * vec2[i][j][k]; sum += res[i][j][k]; }
      res[i][j][hi3-lo3+1] = sum;
      sum = 0;
    }
  return res;
}

int   *   add_const_i_1 (int   *   res, int    cn, int   *   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1;i++) res[i] = cn + vec[i];
  res[hi1-lo1+1] += cn*(hi1-lo1+1);
  return res;
}

int   **  add_const_i_2 (int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) res[i][j] = cn + vec[i][j];
    res[i][hi2-lo2+1] += cn*(hi2-lo2+1);
  }
  return res;
}

int   *** add_const_i_3 (int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) res[i][j][k] = cn + vec[i][j][k];
      res[i][j][hi3-lo3+1] += cn*(hi3-lo3+1);
    }
  return res;
}

int   *   sub_const_i_1 (int   *   res, int    cn, int   *   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1;i++) res[i] = cn - vec[i];
  res[hi1-lo1+1] -= cn*(hi1-lo1+1);
  return res;
}

int   **  sub_const_i_2 (int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) res[i][j] = cn - vec[i][j];
    res[i][hi2-lo2+1] -= cn*(hi2-lo2+1);
  }
  return res;
}

int   *** sub_const_i_3 (int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) res[i][j][k] = cn - vec[i][j][k];
      res[i][j][hi3-lo3+1] -= cn*(hi3-lo3+1);
    }

  return res;
}

int   *   mult_const_i_1 (int   *   res, int    cn, int   *   vec, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = cn * vec[i];
  return res;
}

int   **  mult_const_i_2 (int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = cn * vec[i][j];
  return res;
}

int   *** mult_const_i_3 (int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = cn * vec[i][j][k];
  return res;
}

int   *   add_vec_i_1   (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = vec1[i] + vec2[i];
  return res;
}

int   **  add_vec_i_2   (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = vec1[i][j] + vec2[i][j];
  return res;
}

int   *** add_vec_i_3   (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = vec1[i][j][k] + vec2[i][j][k];
  return res;
}

int   *   sub_vec_i_1   (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1) {
  int i;
  for (i=0;i<=hi1-lo1+1;i++) res[i] = vec1[i] - vec2[i];
  return res;
}

int   **  sub_vec_i_2   (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2+1;j++) res[i][j] = vec1[i][j] - vec2[i][j];
  return res;
}

int   *** sub_vec_i_3   (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) for (k=0;k<=hi3-lo3+1;k++) res[i][j][k] = vec1[i][j][k] - vec2[i][j][k];
  return res;
}

int   *   mult_vec_i_1   (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1) {
  int i;
  int    sum = 0;
  for (i=0;i<=hi1-lo1;i++) { res[i] = vec1[i] * vec2[i]; sum += res[i]; }
  res[hi1-lo1+1] = sum;
  return res;
}

int   **  mult_vec_i_2   (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  int    sum = 0;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) { res[i][j] = vec1[i][j] * vec2[i][j]; sum += res[i][j]; }
    res[i][hi2-lo2+1] = sum;
    sum = 0;
  }
  return res;
}

int   *** mult_vec_i_3   (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  int    sum = 0;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) { res[i][j][k] = vec1[i][j][k] * vec2[i][j][k]; sum += res[i][j][k]; }
      res[i][j][hi3-lo3+1] = sum;
      sum = 0;
    }
  return res;
}















double*   exp_vec_1 (double*   res, double*   vec, int lo1, int hi1) {
  int i;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) { res[i] = exp(vec[i]); sum += res[i]; }
  res[hi1-lo1+1] = sum;
  return res;
}

double**  exp_vec_2 (double**  res, double**  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) { res[i][j] = exp(vec[i][j]); sum += res[i][j]; }
    res[i][hi2-lo2+1] = sum;
    sum = 0;
  }
  return res;
}

double*** exp_vec_3 (double*** res, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) { res[i][j][k] = exp(vec[i][j][k]); sum += res[i][j][k]; }
      res[i][j][hi3-lo3+1] = sum;
      sum = 0;
    }
  return res;
}

double*   log_vec_1 (double*   res, double*   vec, int lo1, int hi1) {
  int i;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) { res[i] = log(vec[i]); sum += res[i]; }
  res[hi1-lo1+1] = sum;
  return res;
}

double**  log_vec_2 (double**  res, double**  vec, int lo1, int hi1, int lo2, int hi2) {
  int i,j;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) {
    for (j=0;j<=hi2-lo2;j++) { res[i][j] = log(vec[i][j]); sum += res[i][j]; }
    res[i][hi2-lo2+1] = sum;
    sum = 0;
  }
  return res;
}

double*** log_vec_3 (double*** res, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3) {
  int i,j,k;
  double sum = 0;
  for (i=0;i<=hi1-lo1;i++) for (j=0;j<=hi2-lo2;j++) {
      for (k=0;k<=hi3-lo3;k++) { res[i][j][k] = log(vec[i][j][k]); sum += res[i][j][k]; }
      res[i][j][hi3-lo3+1] = sum;
      sum = 0;
    }
  return res;
}


double sqrDiff(double*   a, double*   b, int lo1, int hi1) {
  double r;
  int i;
  r = 0;
  for (i=0;i<=hi1-lo1;i++) r += (a[i] - b[i]) * (a[i] - b[i]);
  return r;
}
