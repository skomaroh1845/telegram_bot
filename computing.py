import os
from config import scripts_paths, path_to_venv, path_to_input, path_to_output, user
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
        if input_dir is None:
            self.input_dir = path_to_input
        else:
            self.input_dir = input_dir
        if output_dir is None:
            self.output_dir = path_to_output
        else:
            self.output_dir = output_dir

    def load_from_file(self):
        with open('job_states.txt', 'r') as f:
            for i in self.stages:
                if f.readline().rstrip('\n\r') == 'True':
                    self.stages[i] = True
                else:
                    self.stages[i] = False
            self.curr_stage = int(f.readline().rstrip('\n\r'))
            self.job_num = f.readline().rstrip('\n\r')
            self.input_dir = f.readline().rstrip('\n\r')
            self.output_dir = f.readline().rstrip('\n\r')
            print(self.input_dir, self.output_dir)
            self.output_text = f'last state loaded: curr_step == {self.curr_stage}'


    def save_to_file(self):
        with open('job_states.txt', 'w') as f:
            for i in self.stages:
                f.write(str(self.stages[i]) + '\n')
            f.write(str(self.curr_stage) + '\n')
            f.write(self.job_num + '\n')
            f.write(self.input_dir + '\n')
            f.write(self.output_dir + '\n')


    def start_stage(self, stage_num):
        try:
            os.system(f'ssh {user} ' +
                      f'"sbatch start_python_16cpu.sh -e {path_to_venv} -f {scripts_paths[stage_num]} -i {self.input_dir} -o {self.output_dir}" ' +
                      '> output.txt')
            self.curr_stage = stage_num
            try:
                with open('output.txt', 'r') as f:
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
            os.system(f'ssh {user} "sacct -j {self.job_num}" > output.txt')
            try:
                df = pd.read_table('output.txt')
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
            os.system(f'ssh {user} "cat slurm-{self.job_num}.out" > output.txt')
            try:
                with open('output.txt', 'r') as f:
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
