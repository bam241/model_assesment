#include <TGraph.h>
#include "CLASSLogger.hxx"
#include "Equivalence/EQM_MLP_Kinf.hxx"
#include "EvolutionData.hxx"
#include "IsotopicVector.hxx"

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
  if(!mynfo)
    std::cout << "not able to open " << name << std::endl;
  
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
    std::cout << Z << " " << A << " " << I << " " << name << std::endl;
  } while (!mynfo.eof());
  v_name.pop_back(); //remove additional line
  return v_name;
}

void book_tmva_model(string weight_file) {
  std::cout << "in tmva" << std::endl;
  
  string info_file = replace_extension(weight_file, "nfo");
  input_name = read_nfo(info_file);
  std::cout << "nfo readed" << std::endl;

  reader = new TMVA::Reader("Silent");
  for (int i = 0; i < (int)input_name.size(); i++) {
    input_var.push_back(0);
  }
  
  for (int i = 0; i < (int)input_name.size(); i++) {
    reader->AddVariable(input_name[i].second, &input_var[i]);
  }
  reader->AddVariable("Time", &input_time);

  reader->BookMVA("MLP_EQM", weight_file);
}

void update_tmva_input(IsotopicVector iv, double t) {
  for (int i = 0; i < (int)input_name.size(); i++) {
    input_var[i] = iv.GetQuantity(
        input_name[i].first[0], input_name[i].first[1], input_name[i].first[2]) / iv.GetActinidesComposition().GetSumOfAll();
  //  std::cout << input_name[i].first[0] <<" "<< input_name[i].first[1] <<" "<<  input_name[i].first[2] << " " << input_var[i] << std::endl;
  }

  input_time = t;
}

vector<float> get_compo(IsotopicVector iv){
  vector<float> mycompo = input_var;

  for (int i = 0; i < (int)input_name.size(); i++) {
    mycompo[i] = iv.GetQuantity(
        input_name[i].first[0], input_name[i].first[1], input_name[i].first[2]) / iv.GetActinidesComposition().GetSumOfAll();
  //  std::cout << input_name[i].first[0] <<" "<< input_name[i].first[1] <<" "<<  input_name[i].first[2] << " " << input_var[i] << std::endl;
  }
  return mycompo;
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
  string weight_file = argv[2];
  CLASSLogger* mylog = new CLASSLogger("mylog.log");
  ifstream my_data_idx(argv[1]);
  ofstream output(replace_extension(weight_file, "out"));
  vector<EvolutionData> my_data;
  string line;
  getline(my_data_idx, line);
  int n = 0;

  do {
    my_data.push_back(EvolutionData(mylog, line));
    getline(my_data_idx, line);
    n++;
    if( (n+1) %10 ==0)
      std::cout << n <<"/1000 completed!\r" << std::flush;
  } while (!my_data_idx.eof());
  my_data_idx.close();
  //  my_data.pop_back();

  book_tmva_model(weight_file);
  
  for (int i = 0; i < (int)my_data.size(); i++) {
    IsotopicVector compo = my_data[i].GetIsotopicVectorAt(0.);
    //compo.Print();
    TGraph* keff = my_data[i].GetKeff();
    int n_point = keff->GetN();
    vector<double> time;
    vector<double> kc;
    vector<double> kmlp;
    vector<float> mycompo = get_compo(compo);
  
    for(int j=0; j < (int)mycompo.size(); j++){
      output << mycompo[i] << " ";
    }

    for (int j = 0; j <= n_point; j++) {
      double t_ = 0;
      double kc_ = 0;
      double kmlp_ = 0;
      keff->GetPoint(j, t_, kc_);

      kmlp_ = run_tmva(compo, t_);
      output << " " << kc_ << " " << kmlp_ << " ";
    }
    std::cout << i << std::endl;
    output << std::endl;
  }
  output.close();

  return 0;
}

/*
g++ -o proccess_kinf proccess_kinf.cxx `root-config --cflags` `root-config
--libs`
*/
