#include <tinysvm.h>
#include <stdio.h>
#include <string.h>

int main (int argc, const char* argv[]) {
  TinySVM::Model m;
  char *line;
  char *fields[1024];
  int nFields = 0;
  size_t nbytes;
  int i;
  char *features;
  char *field;

  //printf("loading %s\n", argv[1]);
  if(! m.read(argv[1])) throw;

  line = (char *) malloc (1024 * sizeof(char *));

  while(getline(&line, &nbytes, stdin) != EOF) {
    line = strtok(line, "\n");
    field = strtok(line, "\t");
    features = field;
    //printf("%s\n", features);
    while(field != NULL) {
      printf("%s\t", field);
      field = strtok(NULL, "\t");
    }
    printf("%f\n", m.classify(features));
    fflush(stdout);
  }
}
