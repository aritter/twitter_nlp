#ifndef STATS_H___
#define STATS_H___

#define SQR(x)  ((x)*(x))

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "samplib.h"

double NEGINF;
double epsilonValue;

double factln(double x);
double addLog(double x, double y);

void normalizeLog(double*x, int lo, int hi);

int    sample_Poi(double mu);
int    sample_MultSym(int lo, int hi);
int    sample_Mult(double*th, int lo, int hi);
int    sample_Mult_smooth(double eta, double*th, int lo, int hi);
void   sample_DirSym(double*th, double al, int dim);
void   sample_Dir(double*th, double*al, int dim);
double sample_Gam(double a, double b);
double sample_Bet(double a, double b);
int    sample_Bin(double pi);
double sample_Nor(double mu, double si2);
void   sample_NorMV(double*x, double*mu, double si2, int lo, int hi);
double sample_Exp(double la);
void   sample_Delta(double*dst, double*src, int hi);
double sample_Unif(double lo, double hi);
void   sample_PY(double*pi, double alpha, double delta, int K, double*counts, int*Knew, double**pinew);

int    mode_Poi(double mu);
int    mode_MultSym(int lo, int hi);
int    mode_Mult(double*th, int lo, int hi);
void   mode_DirSym(double*th, double al, int dim);
void   mode_Dir(double*th, double*al, int dim);
double mode_Gam(double a, double b);
double mode_Bet(double a, double b);
int    mode_Bin(double pi);
double mode_Nor(double mu, double si2);
void   mode_NorMV(double*x, double*mu, double si2, int lo, int hi);
double mode_Exp(double la);
void   mode_Delta(double*dst, double*src, int hi);
void   mode_PY(double*pi, double alpha, double delta, int K, double*counts, int*Knew, double**pinew);


double ldf_Poi(int normalize, int x, double la);
double ldf_MultSym(int normalize, int x, int lo, int hi);
double ldf_Mult(int normalize, int x, double*th, int lo, int hi);
double ldf_Mult_smooth(int normalize, double eta, int x, double*th, int lo, int hi);
double ldf_DirSym(int normalize, double*th, double al, int dim);
double ldf_Dir(int normalize, double*th, double*al, int dim);
double ldf_Gam(int normalize, double x, double a, double b);
double ldf_Bet(int normalize, double x, double a, double b);
double ldf_Bin(int normalize, int x, double pi);
double ldf_Nor(int normalize, double x, double mu, double si2);
double ldf_NorMV(int normalize, double*x, double*mu, double si2, int lo, int hi);
double ldf_Exp(int normalize, double x, double la);
double ldf_PY(int normalize, double*pi, double alpha, double delta, int K);

double*   IDR(double*res, int pos, int lo, int hi);
int   *   ID (int   *res, int pos, int lo, int hi);

double*   add_const_r_1 (double*   res, double cn, double*   vec, int lo1, int hi1);
double**  add_const_r_2 (double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2);
double*** add_const_r_3 (double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   add_const_i_1 (int   *   res, int    cn, int   *   vec, int lo1, int hi1);
int   **  add_const_i_2 (int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2);
int   *** add_const_i_3 (int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   sub_const_r_1 (double*   res, double cn, double*   vec, int lo1, int hi1);
double**  sub_const_r_2 (double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2);
double*** sub_const_r_3 (double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   sub_const_i_1 (int   *   res, int    cn, int   *   vec, int lo1, int hi1);
int   **  sub_const_i_2 (int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2);
int   *** sub_const_i_3 (int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   mult_const_r_1(double*   res, double cn, double*   vec, int lo1, int hi1);
double**  mult_const_r_2(double**  res, double cn, double**  vec, int lo1, int hi1, int lo2, int hi2);
double*** mult_const_r_3(double*** res, double cn, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   mult_const_i_1(int   *   res, int    cn, int   *   vec, int lo1, int hi1);
int   **  mult_const_i_2(int   **  res, int    cn, int   **  vec, int lo1, int hi1, int lo2, int hi2);
int   *** mult_const_i_3(int   *** res, int    cn, int   *** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   add_vec_r_1   (double*   res, double*   vec1, double*   vec2, int lo1, int hi1);
double**  add_vec_r_2   (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2);
double*** add_vec_r_3   (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   add_vec_i_1   (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1);
int   **  add_vec_i_2   (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2);
int   *** add_vec_i_3   (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   sub_vec_r_1   (double*   res, double*   vec1, double*   vec2, int lo1, int hi1);
double**  sub_vec_r_2   (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2);
double*** sub_vec_r_3   (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   sub_vec_i_1   (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1);
int   **  sub_vec_i_2   (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2);
int   *** sub_vec_i_3   (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   mult_vec_r_1  (double*   res, double*   vec1, double*   vec2, int lo1, int hi1);
double**  mult_vec_r_2  (double**  res, double**  vec1, double**  vec2, int lo1, int hi1, int lo2, int hi2);
double*** mult_vec_r_3  (double*** res, double*** vec1, double*** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);
int   *   mult_vec_i_1  (int   *   res, int   *   vec1, int   *   vec2, int lo1, int hi1);
int   **  mult_vec_i_2  (int   **  res, int   **  vec1, int   **  vec2, int lo1, int hi1, int lo2, int hi2);
int   *** mult_vec_i_3  (int   *** res, int   *** vec1, int   *** vec2, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   exp_vec_1 (double*   res, double*   vec, int lo1, int hi1);
double**  exp_vec_2 (double**  res, double**  vec, int lo1, int hi1, int lo2, int hi2);
double*** exp_vec_3 (double*** res, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double*   log_vec_1 (double*   res, double*   vec, int lo1, int hi1);
double**  log_vec_2 (double**  res, double**  vec, int lo1, int hi1, int lo2, int hi2);
double*** log_vec_3 (double*** res, double*** vec, int lo1, int hi1, int lo2, int hi2, int lo3, int hi3);

double sqrDiff(double*   a, double*   b, int lo1, int hi1);


int*     load_discrete1(char*fname, int*dim, int*max);
int**    load_discrete2(char*fname, int*dim1, int**dim2, int*max);
int***   load_discrete3(char*fname, int*dim1, int**dim2, int***dim3, int*max);
int****  load_discrete4(char*fname, int*dim1, int**dim2, int***dim3, int****dim4, int*max);
double** load_matrix(char*fname, int*N, int*dim);
int**    load_matrix_int(char*fname, int*N, int*dim);

int* string2array(char*input, int*dim);

#endif
