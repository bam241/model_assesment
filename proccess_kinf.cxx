#include <TGraph.h>
#include "CLASSLogger.hxx"
#include "Equivalence/EQM_MLP_Kinf.hxx"
#include "EvolutionData.hxx"

#include <TMVA/Reader.h>

#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

vector<float> input_var;
float input_time;
TMVA::Reader* reader;
vector<pair<vector<int>, string> > input_name;

string replace_extension(string filename, string new_extension) {
  size_t lastindex = filename.find_last_of(".");
  string rawname = filename.substr(0, lastindex);
  filename = rawname + "." + new_extension;
  return filename;
}

vector<pair<vector<int>, string> > read_nfo(string name) {
  ifstream mynfo(name);
  vector<pair<vector<int>, string> > v_name;
  do {
    int Z, A, I;
    string name;
    mynfo >> Z >> A >> I >> name;
    vector<int> zai;
    zai.push_back(Z);
    zai.push_back(A);
    zai.push_back(I);
    v_name.push_back(pair<vector<int>, string>(zai, name));
  } while (mynfo.eof());
  return v_name;
}

void book_tmva_model(string weight_file) {
  string info_file = replace_extension(weight_file, "nfo");
  input_name = read_nfo(info_file);

  reader = new TMVA::Reader("Silent");
  for (int i = 0; i < (int)input_name.size(); i++) {
    input_var.push_back(0);
    reader->AddVariable(input_name[i].second, &input_var[i]);
  }
  reader->AddVariable("Time", &input_time);

  reader->BookMVA("MLP_EQM", weight_file);
}

void update_tmva_input(IsotopicVector iv, double t) {
  for (int i = 0; i < (int)input_name.size(); i++) {
    input_var[i] = iv.GetQuantity(
        input_name[i].first[0], input_name[i].first[1], input_name[i].first[2]);
  }

  input_time = t;
}

double run_tmva(IsotopicVector iv, double t) {
  update_tmva_input(iv, t);

  double val = (double)(reader->EvaluateRegression("MLP_EQM"))[0];

  return val;  // retourn k_{inf}(t = Time)
}

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cout << "Bad arg number: usage dat_list mlp_weight" << std::endl;
    return 1;
  }

  CLASSLogger* mylog = new CLASSLogger("mylog.log");

  ifstream my_data_idx(argv[1]);
  vector<EvolutionData> my_data;
  string line;
  getline(my_data_idx, line);
  do {
    my_data.push_back(EvolutionData(mylog, line));
    getline(my_data_idx, line);
  } while (!my_data_idx.eof());

  book_tmva_model(argv[1]);

  for (int i = 0; i <= (int)my_data.size(); i++) {
    IsotopicVector compo = my_data[i].GetIsotopicVectorAt(0.);
    TGraph* keff = my_data[i].GetKeff();
    int n_point = keff->GetN();
    vector<double> time;
    vector<double> kc;
    vector<double> kmlp;

    for (int j = 0; j <= n_point; j++) {
      double t_ = 0;
      double kc_ = 0;
      double kmlp_ = 0;
      keff->GetPoint(j, t_, kc_);

      kmlp_ = run_tmva(compo, t_);
      std::cout << t_ << " " << kc_ << " " << kmlp_ << std::endl;
    }
  }

  return 0;
}

/*
g++ -o proccess_kinf proccess_kinf.cxx `root-config --cflags` `root-config
--libs`
*/
