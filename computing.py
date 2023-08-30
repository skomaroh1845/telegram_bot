import os
from config import scripts_paths, path_to_venv, path_to_input, path_to_output, user
import pandas as pd

class Computing:

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
        self.curr_stage = 1
        self.job_num = ''
        if input_dir is None:
            self.input = path_to_input
        else:
            self.input = input_dir
        if output_dir is None:
            self.output = path_to_output
        else:
            self.output = output_dir

    def start_stage(self):
        if self.stages[self.curr_stage] == True:
            self.curr_stage += 1
        try:
            os.system(f'ssh {user} ' +
                      f'"sbatch start_python_16cpu.sh -e {path_to_venv} -f {scripts_paths[self.curr_stage]} -i {path_to_input} -o {path_to_output}" ' +
                      '> output.txt')
            try:
                with open('output.txt', 'r') as f:
                    text = f.read()
                    self.job_num = text.split(' ')[-1]
                    return f'Stage {self.curr_stage}: ' + text
            except:
                return f'Stage {self.curr_stage}: output file cannot be read'
        except:
            return f'Stage {self.curr_stage}: "sbatch" was not executed'


    def check_curr_job(self):
        try:
            os.system(f'ssh {user} "sacct -j {self.job_num}" > output.txt')
            try:
                df = pd.read_table('output.txt')
                return df.loc[2, 'State']
            except:
                return f'job {self.job_num}: output file cannot be read'
        except:
            return f'job {self.job_num}: "sacct" was not executed'


    def get_job_feed_back(self):
        try:
            os.system(f'ssh {user} "cat slurm-{self.job_num}.out" > output.txt')
            try:
                with open('output.txt', 'r') as f:
                    text = f.read()
                    return f'Stage {self.curr_stage} feed back:'+ '\n' + text
            except:
                return f'Stage {self.curr_stage}: output file cannot be read'
        except:
            return f'Stage {self.curr_stage}: "cat slurm.out" was not executed'


    def terminate_job(self):
        try:
            os.system(f'ssh {user} "scancel {self.job_num}"')
        except:
            return f'job {self.job_num}: "scancel" was not executed'
