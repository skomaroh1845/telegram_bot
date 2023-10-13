import os
from config import scripts_paths, path_to_venv, path_to_input, path_to_output, user, NUM_OF_INSTANCE
import pandas as pd


class Computer:

    def __init__(self, input_dir=None, output_dir=None):
        self.stages = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: False,
            8: False,
            9: False,
            10: False,
            11: False,
            12: False,
            13: False,
            14: False,
            15: False
        }
        self.curr_stage = 0
        self.job_num = ''
        self.output_text = ''
        self.running = False
        self.r_site = ''
        self.in_list = []
        self.out_list = []
        self.sample_names = []
        self.curr_sample = 0
        if input_dir is None:
            self.input_dir = path_to_input
        else:
            self.input_dir = input_dir
        if output_dir is None:
            self.output_dir = path_to_output
        else:
            self.output_dir = output_dir

    def set_dir_lists(self, dirs):
        for dir in dirs:
            self.sample_names.append(dir + '_' + self.r_site.split('_')[0].split('-')[0])
            self.in_list.append(self.input_dir + '/' + dir)
            self.out_list.append(self.output_dir + '/' + dir + '/' + self.r_site.split('_')[0].split('-')[0])
        print(self.in_list)
        print(self.out_list)

    def add_r_site(self, site):
        part1 = site.split('/')[0]
        r2_start = site.split('/')[1]
        if self.r_site != '':
            self.r_site = self.r_site + '_'
        self.r_site = self.r_site + part1 + r2_start + '-' + r2_start
        print(self.r_site)

    def load_from_file(self):
        with open(f'job_states{NUM_OF_INSTANCE}.txt', 'r') as f:
            for i in self.stages:
                if f.readline().rstrip('\n\r') == 'True':
                    self.stages[i] = True
                else:
                    self.stages[i] = False
            self.curr_stage = int(f.readline().rstrip('\n\r'))
            self.job_num = f.readline().rstrip('\n\r')
            self.input_dir = f.readline().rstrip('\n\r')
            self.output_dir = f.readline().rstrip('\n\r')
            self.r_site = f.readline().rstrip('\n\r')
            self.curr_sample = int(f.readline().rstrip('\n\r'))
            num_of_samples = int(f.readline().rstrip('\n\r'))
            for i in range(num_of_samples):
                self.sample_names.append(f.readline().rstrip('\n\r'))
                self.in_list.append(f.readline().rstrip('\n\r'))
                self.out_list.append(f.readline().rstrip('\n\r'))
            print(self.input_dir, self.output_dir)
            self.output_text = f'last state loaded: curr_step == {self.curr_stage} \n curr_sample == {self.sample_names[self.curr_sample]}'


    def save_to_file(self):
        with open(f'job_states{NUM_OF_INSTANCE}.txt', 'w') as f:
            for i in self.stages:
                f.write(str(self.stages[i]) + '\n')
            f.write(str(self.curr_stage) + '\n')
            f.write(self.job_num + '\n')
            f.write(self.input_dir + '\n')
            f.write(self.output_dir + '\n')
            f.write(self.r_site + '\n')
            f.write(str(self.curr_sample) + '\n')
            f.write(str(len(self.sample_names)) + '\n')  # write num of samples
            for i in range(len(self.sample_names)):
                f.write(self.sample_names[i] + '\n')
                f.write(self.in_list[i] + '\n')
                f.write(self.out_list[i] + '\n')



    def start_stage(self, stage_num):
        try:
            os.system(f'ssh {user} ' +
                    f'"sbatch start_python_8cpu.sh -e {path_to_venv} -f {scripts_paths[stage_num]} -i {self.in_list[self.curr_sample]} -o {self.out_list[self.curr_sample]} -r {self.r_site}" ' +
                      f'> output{NUM_OF_INSTANCE}.txt')
            self.curr_stage = stage_num
            try:
                with open(f'output{NUM_OF_INSTANCE}.txt', 'r') as f:
                    text = f.read()
                    self.job_num = text.split(' ')[-1].strip('\n')
                    self.output_text = f'Stage {stage_num}: ' + text
            except:
                self.output_text = f'Stage {stage_num}: output file cannot be read'
        except:
            self.output_text = f'Stage {stage_num}: "sbatch" was not executed'


    def check_curr_job_state(self):
        if self.job_num == '':
            self.output_text = ''
            return
        try:
            os.system(f'ssh {user} "sacct -j {self.job_num}" > output{NUM_OF_INSTANCE}.txt')
            try:
                df = pd.read_table(f'output{NUM_OF_INSTANCE}.txt')
                if len(df) >= 2:
                    array = str(df.iloc[1, 0]).split(' ')
                    array = [i for i in array if i]
                    self.output_text = array[5]
                    if self.output_text == 'COMPLETED':
                        self.stages[self.curr_stage] = True
                else:
                    self.output_text = 'empty'
            except:
                self.output_text = f'job {self.job_num}: output file cannot be read'
        except:
            self.output_text = f'job {self.job_num}: "sacct" was not executed'


    def get_job_output(self):
        if self.job_num == '':
            return
        try:
            os.system(f'ssh {user} "cat slurm-{self.job_num}.out" > output{NUM_OF_INSTANCE}.txt')
            try:
                with open(f'output{NUM_OF_INSTANCE}.txt', 'r') as f:
                    text = f.read()
                    self.output_text = f'Stage {self.curr_stage} feed back:'+ '\n' + text
            except:
                self.output_text = f'Stage {self.curr_stage}: output file cannot be read'
        except:
            self.output_text = f'Stage {self.curr_stage}: "cat slurm.out" was not executed'


    def terminate_job(self):
        if self.job_num == '':
            return
        try:
            os.system(f'ssh {user} "scancel {self.job_num}"')
            self.output_text = f'Stage {self.curr_stage}: job {self.job_num} was canceled'
        except:
            self.output_text = f'Stage {self.curr_stage}: job {self.job_num}: "scancel" was not executed'
